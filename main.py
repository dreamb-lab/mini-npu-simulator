import json
import time


# ---------------------------------
# MAC 계산 함수
# ---------------------------------

def calculate_mac(matrix, filter_matrix):
    score = 0

    # 입력 행렬과 필터의 같은 위치 숫자를 곱한 뒤 모두 더하기
    for i in range(len(matrix)):
        for j in range(len(matrix)):
            score += matrix[i][j] * filter_matrix[i][j]

    return score


# ---------------------------------
# 결과 판정 함수
# ---------------------------------

def classify(cross_score, x_score):

    # 두 점수의 차이가 매우 작으면 동점으로 처리
    if abs(cross_score - x_score) < 1e-9:
        return "UNDECIDED"

    # Cross 점수가 더 크면 Cross
    elif cross_score > x_score:
        return "Cross"

    # X 점수가 더 크면 X
    else:
        return "X"


# ---------------------------------
# 사용자 입력 모드 (3x3)
# ---------------------------------

def run_user_mode():
    print("\n[User Input Mode]")

    # Cross 필터 입력
    print("Enter Cross filter (3 rows, 3 numbers per row):")
    cross_filter = read_matrix()
    print("Cross filter saved.")

    # X 필터 입력
    print("Enter X filter (3 rows, 3 numbers per row):")
    x_filter = read_matrix()
    print("X filter saved.")

    # 분석할 패턴 입력
    print("Enter input pattern (3 rows, 3 numbers per row):")
    matrix = read_matrix()

    # 두 필터의 MAC 점수 계산
    cross_score = calculate_mac(matrix, cross_filter)
    x_score = calculate_mac(matrix, x_filter)

    # 계산 결과 출력
    print("Cross score:", cross_score)
    print("X score:", x_score)
    print("Result:", classify(cross_score, x_score))

    # MAC 연산 시간 측정 (10회 반복)
    repeat = 10
    start = time.perf_counter()

    for _ in range(repeat):
        calculate_mac(matrix, cross_filter)

    end = time.perf_counter()

    # 평균 실행 시간 계산 (밀리초)
    average_time = (end - start) / repeat * 1000

    print("Average MAC time:", average_time, "ms")


# ---------------------------------
# 3x3 행렬 입력 및 검사 함수
# ---------------------------------

def read_matrix():
    matrix = []

    # 정확히 3개의 행을 입력받을 때까지 반복
    while len(matrix) < 3:
        try:
            row = [float(x) for x in input().split()]

            # 한 행에 숫자가 3개인지 확인
            if len(row) != 3:
                print("Please enter exactly 3 numbers.")
                continue

            matrix.append(row)

        # 숫자가 아닌 값을 입력하면 오류 안내
        except ValueError:
            print("Invalid input. Please enter numbers only.")

    return matrix


# ---------------------------------
# JSON 분석 모드
# ---------------------------------

def run_json_mode():
    print("\n[JSON Analysis Mode]")

    # JSON 파일 읽기
    try:
        with open("data.json", "r") as file:
            data = json.load(file)

    # 파일이 없거나 JSON 형식이 잘못된 경우
    except (FileNotFoundError, json.JSONDecodeError):
        print("Error: data.json is missing or invalid.")
        return

    # 테스트 결과 집계 변수
    total_tests = 0
    pass_count = 0
    fail_count = 0
    failed_cases = []

    # JSON에 저장된 모든 테스트 반복
    for test_name, test_case in data["patterns"].items():
        print("\nTest:", test_name)

        try:
            # 입력 행렬과 정답 가져오기
            matrix = test_case["input"]
            expected = test_case["expected"]

            # 정답 이름을 통일
            if expected == "+":
                expected = "Cross"
            elif expected == "x":
                expected = "X"

            # 테스트 이름에서 행렬 크기 확인
            size_key = test_name.rsplit("_", 1)[0]

            # 해당 크기에 맞는 필터 선택
            cross_filter = data["filters"][size_key]["cross"]
            x_filter = data["filters"][size_key]["x"]

            size = len(matrix)

            # 입력 행렬과 필터의 크기 검사
            if size == 0:
                raise ValueError("Matrix is empty.")

            if len(cross_filter) != size or len(x_filter) != size:
                raise ValueError("Matrix and filter sizes do not match.")

            # 각 행의 열 개수 검사
            if any(len(row) != size for row in matrix):
                raise ValueError("Invalid input matrix dimensions.")

            if any(len(row) != size for row in cross_filter):
                raise ValueError("Invalid Cross filter dimensions.")

            if any(len(row) != size for row in x_filter):
                raise ValueError("Invalid X filter dimensions.")

            # Cross와 X의 MAC 점수 계산
            cross_score = calculate_mac(matrix, cross_filter)
            x_score = calculate_mac(matrix, x_filter)

            # 점수를 비교하여 최종 결과 판정
            result = classify(cross_score, x_score)

            # 테스트 결과 출력
            print("Cross score:", cross_score)
            print("X score:", x_score)
            print("Expected:", expected)
            print("Result:", result)

            # PASS / FAIL 판정
            total_tests += 1

            if result == expected:
                print("PASS")
                pass_count += 1

            else:
                print("FAIL")
                fail_count += 1
                failed_cases.append(test_name)

                # 실패 원인 출력
                if result == "UNDECIDED":
                    print("Reason: Cross and X scores are equal.")
                else:
                    print("Reason: Decision does not match expected label.")

        # 데이터 오류가 발생해도 프로그램 전체가 종료되지 않도록 처리
        except (KeyError, TypeError, ValueError, IndexError) as error:
            print("FAIL")
            print("Reason:", error)
            fail_count += 1
            failed_cases.append(test_name)

    # ---------------------------------
    # 전체 테스트 결과 요약
    # ---------------------------------

    print("\nTotal tests:", total_tests)
    print("Passed:", pass_count)
    print("Failed:", fail_count)
    print("Failed cases:", failed_cases)

    # ---------------------------------
    # 성능 측정
    # ---------------------------------

    print("\nPerformance Analysis")
    print("Size\tAverage Time (ms)\tOperations")

    # 5x5, 13x13, 25x25 행렬 성능 측정
    for size_key in ["size_5", "size_13", "size_25"]:

        # 해당 크기의 테스트 데이터 가져오기
        test_name = size_key + "_1"
        matrix = data["patterns"][test_name]["input"]
        cross_filter = data["filters"][size_key]["cross"]

        # MAC 연산을 10회 반복하여 평균 시간 계산
        repeat = 10
        start = time.perf_counter()

        for _ in range(repeat):
            calculate_mac(matrix, cross_filter)

        end = time.perf_counter()

        # 초 단위를 밀리초로 변환
        average_time = (end - start) / repeat * 1000

        # 연산 횟수 N x N 계산
        size = len(matrix)
        operations = size * size

        print(f"{size}x{size}\t{average_time:.6f}\t\t{operations}")


# ---------------------------------
# 프로그램 시작 및 모드 선택
# ---------------------------------

print("Mini NPU Simulator")
print()
print("Select Mode")
print("1. User Input Mode (3x3)")
print("2. JSON Analysis Mode")

# 올바른 모드를 입력할 때까지 반복
while True:
    mode = input("Enter mode (1 or 2): ")

    if mode == "1":
        run_user_mode()
        break

    elif mode == "2":
        run_json_mode()
        break

    else:
        print("Invalid mode. Please enter 1 or 2.")