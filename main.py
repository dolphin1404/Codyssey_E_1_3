"""
Mini NPU Simulator
- MAC(Multiply-Accumulate) 연산 기반 패턴 판별 시뮬레이터
- 모드 1: 사용자 입력 (3×3)
- 모드 2: data.json 분석
- 보너스: 메모리 최적화(1D 배열), 패턴 생성기
"""

import json
import time
import os


# ──────────────────────────────────────────────
# 라벨 정규화
# ──────────────────────────────────────────────

def normalize_label(label):
    """표준 라벨로 정규화: '+' → 'Cross', 'x'/'X' → 'X', 'cross' → 'Cross'"""
    label_lower = label.strip().lower()
    if label_lower in ('+', 'cross', '십자가'):
        return 'Cross'
    elif label_lower in ('x',):
        return 'X'
    return label


# ──────────────────────────────────────────────
# MAC 연산 (2D - 기본)
# ──────────────────────────────────────────────

def mac_operation(pattern, filter_data):
    """2D 배열 MAC 연산: 위치별 곱의 합"""
    n = len(pattern)
    score = 0.0
    for i in range(n):
        for j in range(n):
            score += pattern[i][j] * filter_data[i][j]
    return score


# ──────────────────────────────────────────────
# MAC 연산 (1D - 보너스: 메모리 최적화)
# ──────────────────────────────────────────────

def flatten_2d(matrix):
    """2D 배열을 1D 배열로 변환"""
    result = []
    for row in matrix:
        for val in row:
            result.append(val)
    return result


def mac_operation_1d(pattern_1d, filter_1d):
    """1D 배열 MAC 연산"""
    score = 0.0
    for i in range(len(pattern_1d)):
        score += pattern_1d[i] * filter_1d[i]
    return score


# ──────────────────────────────────────────────
# 점수 비교 (부동소수점 허용오차)
# ──────────────────────────────────────────────

EPSILON = 1e-9


def compare_scores(score_a, score_b):
    """
    두 점수를 비교하여 판정 결과를 반환한다.
    |score_a - score_b| < EPSILON 이면 동점(UNDECIDED)
    """
    diff = abs(score_a - score_b)
    if diff < EPSILON:
        return 'UNDECIDED'
    elif score_a > score_b:
        return 'A'
    else:
        return 'B'


# ──────────────────────────────────────────────
# 보너스: 패턴 생성기
# ──────────────────────────────────────────────

def generate_cross_pattern(n):
    """N×N 십자가(Cross) 패턴 자동 생성"""
    mid = n // 2
    pattern = [[0] * n for _ in range(n)]
    for i in range(n):
        pattern[mid][i] = 1  # 가운데 행
        pattern[i][mid] = 1  # 가운데 열
    return pattern


def generate_x_pattern(n):
    """N×N X 패턴 자동 생성"""
    pattern = [[0] * n for _ in range(n)]
    for i in range(n):
        pattern[i][i] = 1          # 주대각선
        pattern[i][n - 1 - i] = 1  # 부대각선
    return pattern


# ──────────────────────────────────────────────
# 입력 처리 유틸리티
# ──────────────────────────────────────────────

def input_matrix(name, size=3):
    """콘솔에서 size×size 행렬을 입력받는다. 검증 실패 시 재입력 유도."""
    while True:
        print(f"{name} ({size}줄 입력, 공백 구분)")
        matrix = []
        valid = True

        for row_idx in range(size):
            line = input().strip()
            parts = line.split()

            # 열 수 검증
            if len(parts) != size:
                print(f"입력 형식 오류: 각 줄에 {size}개의 숫자를 공백으로 구분해 입력하세요.")
                valid = False
                break

            # 숫자 파싱 검증
            row = []
            for p in parts:
                try:
                    row.append(float(p))
                except ValueError:
                    print(f"입력 형식 오류: '{p}'은(는) 유효한 숫자가 아닙니다. 다시 입력하세요.")
                    valid = False
                    break
            if not valid:
                break
            matrix.append(row)

        if valid and len(matrix) == size:
            return matrix

        print(f"다시 입력해 주세요.\n")


def print_matrix(matrix, indent="  "):
    """행렬을 보기 좋게 출력"""
    for row in matrix:
        print(indent + " ".join(f"{v:g}" for v in row))


def print_separator():
    print("#" + "-" * 39)


# ──────────────────────────────────────────────
# 성능 측정
# ──────────────────────────────────────────────

def measure_mac_time(pattern, filter_data, repeat=10):
    """MAC 연산 시간을 repeat회 반복 측정하여 평균(ms) 반환"""
    times = []
    for _ in range(repeat):
        start = time.perf_counter()
        mac_operation(pattern, filter_data)
        end = time.perf_counter()
        times.append((end - start) * 1000)  # ms 변환
    avg = sum(times) / len(times)
    return avg


def measure_mac_time_1d(pattern_1d, filter_1d, repeat=10):
    """1D MAC 연산 시간을 repeat회 반복 측정하여 평균(ms) 반환"""
    times = []
    for _ in range(repeat):
        start = time.perf_counter()
        mac_operation_1d(pattern_1d, filter_1d)
        end = time.perf_counter()
        times.append((end - start) * 1000)
    avg = sum(times) / len(times)
    return avg


# ──────────────────────────────────────────────
# 모드 1: 사용자 입력 (3×3)
# ──────────────────────────────────────────────

def mode_user_input():
    """사용자가 3×3 필터 2개와 패턴을 입력하여 MAC 연산 수행"""
    print_separator()
    print("# [1] 필터 입력")
    print_separator()

    filter_a = input_matrix("필터 A", 3)
    print()
    filter_b = input_matrix("필터 B", 3)

    print_separator()
    print("# [2] 패턴 입력")
    print_separator()

    pattern = input_matrix("패턴", 3)

    # MAC 연산
    score_a = mac_operation(pattern, filter_a)
    score_b = mac_operation(pattern, filter_b)

    # 시간 측정 (10회 평균)
    avg_time_a = measure_mac_time(pattern, filter_a, 10)
    avg_time_b = measure_mac_time(pattern, filter_b, 10)
    avg_time = (avg_time_a + avg_time_b) / 2

    # 판정
    result = compare_scores(score_a, score_b)

    print()
    print_separator()
    print("# [3] MAC 결과")
    print_separator()
    print(f"A 점수: {score_a}")
    print(f"B 점수: {score_b}")
    print(f"연산 시간(평균/10회): {avg_time:.3f} ms")

    if result == 'UNDECIDED':
        print(f"판정: 판정 불가 (|A-B| < {EPSILON})")
    else:
        print(f"판정: {result}")

    # 성능 분석 (3×3)
    print()
    print_separator()
    print("# [4] 성능 분석 (3×3)")
    print_separator()
    print(f"{'크기':<8} {'평균 시간(ms)':<15} {'연산 횟수'}")
    print("-" * 37)

    n = 3
    avg = measure_mac_time(pattern, filter_a, 10)
    print(f"{n}x{n:<6} {avg:<15.3f} {n*n}")

    # 보너스: 1D 최적화 비교
    print()
    print_separator()
    print("# [보너스] 2D vs 1D 성능 비교 (3×3)")
    print_separator()

    pattern_1d = flatten_2d(pattern)
    filter_a_1d = flatten_2d(filter_a)

    avg_2d = measure_mac_time(pattern, filter_a, 10)
    avg_1d = measure_mac_time_1d(pattern_1d, filter_a_1d, 10)

    print(f"{'방식':<10} {'평균 시간(ms)'}")
    print("-" * 30)
    print(f"{'2D 배열':<10} {avg_2d:.3f}")
    print(f"{'1D 배열':<10} {avg_1d:.3f}")

    # 보너스: 패턴 생성기 안내
    print()
    print_separator()
    print("# [보너스] 패턴 생성기")
    print_separator()

    while True:
        gen_input = input("패턴 생성기를 사용하시겠습니까? (y/n): ").strip().lower()
        if gen_input == 'y':
            try:
                gen_size = int(input("생성할 패턴 크기 N을 입력하세요 (홀수): ").strip())
                if gen_size < 3 or gen_size % 2 == 0:
                    print("3 이상의 홀수를 입력하세요.")
                    continue
            except ValueError:
                print("유효한 숫자를 입력하세요.")
                continue

            cross_p = generate_cross_pattern(gen_size)
            x_p = generate_x_pattern(gen_size)

            print(f"\n생성된 Cross 패턴 ({gen_size}x{gen_size}):")
            print_matrix(cross_p)
            print(f"\n생성된 X 패턴 ({gen_size}x{gen_size}):")
            print_matrix(x_p)

            # 생성된 패턴으로 MAC 연산 수행
            cross_filter = generate_cross_pattern(gen_size)
            x_filter = generate_x_pattern(gen_size)

            score_cross_cross = mac_operation(cross_p, cross_filter)
            score_cross_x = mac_operation(cross_p, x_filter)
            score_x_cross = mac_operation(x_p, cross_filter)
            score_x_x = mac_operation(x_p, x_filter)

            print(f"\n[Cross 패턴 판정]")
            print(f"  Cross 필터 점수: {score_cross_cross}")
            print(f"  X 필터 점수: {score_cross_x}")
            r = compare_scores(score_cross_cross, score_cross_x)
            if r == 'A':
                print(f"  판정: Cross")
            elif r == 'B':
                print(f"  판정: X")
            else:
                print(f"  판정: UNDECIDED")

            print(f"\n[X 패턴 판정]")
            print(f"  Cross 필터 점수: {score_x_cross}")
            print(f"  X 필터 점수: {score_x_x}")
            r = compare_scores(score_x_cross, score_x_x)
            if r == 'A':
                print(f"  판정: Cross")
            elif r == 'B':
                print(f"  판정: X")
            else:
                print(f"  판정: UNDECIDED")

            # 성능 측정
            avg = measure_mac_time(cross_p, cross_filter, 10)
            print(f"\n  연산 시간(평균/10회): {avg:.3f} ms")
            print(f"  연산 횟수: {gen_size * gen_size}")
            break
        elif gen_input == 'n':
            break
        else:
            print("y 또는 n을 입력하세요.")


# ──────────────────────────────────────────────
# 모드 2: data.json 분석
# ──────────────────────────────────────────────

def mode_json_analysis():
    """data.json에서 필터와 패턴을 로드하여 일괄 판정"""

    # JSON 로드
    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"오류: {json_path} 파일을 찾을 수 없습니다.")
        return
    except json.JSONDecodeError as e:
        print(f"오류: data.json 파싱 실패 - {e}")
        return

    # ── [1] 필터 로드 ──
    print_separator()
    print("# [1] 필터 로드")
    print_separator()

    filters = {}
    filter_section = data.get("filters", {})

    for size_key, filter_data in filter_section.items():
        try:
            n = int(size_key.split("_")[1])
        except (IndexError, ValueError):
            print(f"  [ERR] {size_key} 필터 키 파싱 실패")
            continue

        loaded = {}
        for label_key, matrix in filter_data.items():
            std_label = normalize_label(label_key)
            loaded[std_label] = matrix

        filters[size_key] = {"n": n, "filters": loaded}
        labels = ", ".join(loaded.keys())
        print(f"  [OK] {size_key} 필터 로드 완료 ({labels})")

    # ── [2] 패턴 분석 ──
    print()
    print_separator()
    print("# [2] 패턴 분석 (라벨 정규화 적용)")
    print_separator()

    patterns = data.get("patterns", {})
    results = []  # (케이스명, 판정, expected, pass/fail, 사유)
    size_patterns = {}  # 성능 분석용 데이터 수집

    for pattern_key in sorted(patterns.keys()):
        pattern_info = patterns[pattern_key]
        print(f"\n  --- {pattern_key} ---")

        # 키에서 N 추출
        try:
            parts = pattern_key.split("_")
            n = int(parts[1])
            size_key = f"size_{n}"
        except (IndexError, ValueError):
            reason = f"패턴 키 '{pattern_key}' 에서 크기를 추출할 수 없음"
            print(f"  판정: FAIL ({reason})")
            results.append((pattern_key, "ERROR", "?", "FAIL", reason))
            continue

        # 필터 존재 여부 확인
        if size_key not in filters:
            reason = f"해당 크기의 필터({size_key})가 존재하지 않음"
            print(f"  판정: FAIL ({reason})")
            results.append((pattern_key, "ERROR", "?", "FAIL", reason))
            continue

        filter_info = filters[size_key]
        input_data = pattern_info.get("input", [])
        expected_raw = pattern_info.get("expected", "")
        expected = normalize_label(expected_raw)

        # 크기 검증
        input_rows = len(input_data)
        input_cols = len(input_data[0]) if input_data else 0

        if input_rows != n or input_cols != n:
            reason = f"크기 불일치: 기대 {n}x{n}, 실제 {input_rows}x{input_cols}"
            print(f"  판정: FAIL ({reason})")
            results.append((pattern_key, "ERROR", expected, "FAIL", reason))
            continue

        # 필터 크기 검증
        cross_filter = filter_info["filters"].get("Cross")
        x_filter = filter_info["filters"].get("X")

        if cross_filter is None or x_filter is None:
            reason = f"Cross 또는 X 필터가 누락됨"
            print(f"  판정: FAIL ({reason})")
            results.append((pattern_key, "ERROR", expected, "FAIL", reason))
            continue

        if len(cross_filter) != n or len(x_filter) != n:
            reason = f"필터 크기 불일치"
            print(f"  판정: FAIL ({reason})")
            results.append((pattern_key, "ERROR", expected, "FAIL", reason))
            continue

        # MAC 연산
        score_cross = mac_operation(input_data, cross_filter)
        score_x = mac_operation(input_data, x_filter)

        print(f"  Cross 점수: {score_cross}")
        print(f"  X 점수: {score_x}")

        # 판정
        if abs(score_cross - score_x) < EPSILON:
            judgment = "UNDECIDED"
        elif score_cross > score_x:
            judgment = "Cross"
        else:
            judgment = "X"

        # PASS/FAIL
        if judgment == expected:
            pf = "PASS"
            reason = ""
        elif judgment == "UNDECIDED":
            pf = "FAIL"
            reason = "동점 규칙"
        else:
            pf = "FAIL"
            reason = f"판정 {judgment} != expected {expected}"

        pf_display = pf
        if reason:
            pf_display = f"{pf} ({reason})"

        print(f"  판정: {judgment} | expected: {expected} | {pf_display}")
        results.append((pattern_key, judgment, expected, pf, reason))

        # 성능 분석용 데이터 수집
        if n not in size_patterns:
            size_patterns[n] = (input_data, cross_filter)

    # ── [3] 성능 분석 ──
    print()
    print_separator()
    print("# [3] 성능 분석 (평균/10회)")
    print_separator()

    print(f"  {'크기':<8} {'평균 시간(ms)':<15} {'연산 횟수'}")
    print("  " + "-" * 37)

    # 3×3은 생성기로 만들어서 측정
    cross_3 = generate_cross_pattern(3)
    x_3 = generate_x_pattern(3)
    avg_3 = measure_mac_time(cross_3, x_3, 10)
    print(f"  {'3x3':<8} {avg_3:<15.3f} {9}")

    perf_data = [(3, avg_3, 9)]

    for n in sorted(size_patterns.keys()):
        pat, flt = size_patterns[n]
        avg = measure_mac_time(pat, flt, 10)
        print(f"  {n}x{n:<6} {avg:<15.3f} {n*n}")
        perf_data.append((n, avg, n * n))

    # 보너스: 2D vs 1D 성능 비교
    print()
    print_separator()
    print("# [보너스] 2D vs 1D 메모리 최적화 성능 비교")
    print_separator()

    print(f"  {'크기':<8} {'2D 시간(ms)':<14} {'1D 시간(ms)':<14} {'차이'}")
    print("  " + "-" * 50)

    # 3×3
    cross_3_1d = flatten_2d(cross_3)
    x_3_1d = flatten_2d(x_3)
    avg_2d_3 = measure_mac_time(cross_3, x_3, 10)
    avg_1d_3 = measure_mac_time_1d(cross_3_1d, x_3_1d, 10)
    diff_3 = avg_2d_3 - avg_1d_3
    print(f"  {'3x3':<8} {avg_2d_3:<14.3f} {avg_1d_3:<14.3f} {diff_3:+.3f}")

    for n in sorted(size_patterns.keys()):
        pat, flt = size_patterns[n]
        pat_1d = flatten_2d(pat)
        flt_1d = flatten_2d(flt)

        avg_2d = measure_mac_time(pat, flt, 10)
        avg_1d = measure_mac_time_1d(pat_1d, flt_1d, 10)
        diff = avg_2d - avg_1d
        print(f"  {n}x{n:<6} {avg_2d:<14.3f} {avg_1d:<14.3f} {diff:+.3f}")

    # ── [4] 결과 요약 ──
    print()
    print_separator()
    print("# [4] 결과 요약")
    print_separator()

    total = len(results)
    passed = sum(1 for r in results if r[3] == "PASS")
    failed = total - passed

    print(f"  총 테스트: {total}개")
    print(f"  통과: {passed}개")
    print(f"  실패: {failed}개")

    if failed > 0:
        print()
        print("  실패 케이스:")
        for case_name, judgment, expected, pf, reason in results:
            if pf == "FAIL":
                display_reason = reason if reason else f"판정 {judgment} != expected {expected}"
                print(f"    - {case_name}: {display_reason}")
    else:
        print()
        print("  모든 테스트를 통과했습니다.")

    print()
    print("  (상세 원인 분석 및 복잡도 설명은 README.md의 \"결과 리포트\" 섹션에 작성)")


# ──────────────────────────────────────────────
# 메인 실행
# ──────────────────────────────────────────────

def main():
    print("=== Mini NPU Simulator ===")
    print()
    print("[모드 선택]")
    print("1. 사용자 입력 (3x3)")
    print("2. data.json 분석")

    while True:
        choice = input("선택: ").strip()
        if choice == '1':
            mode_user_input()
            break
        elif choice == '2':
            mode_json_analysis()
            break
        else:
            print("1 또는 2를 입력하세요.")


if __name__ == "__main__":
    main()
