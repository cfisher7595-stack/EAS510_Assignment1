"""
EAS 510 - Expert System Rules
"""
import os


def rule1_metadata(target_info, input_path):
    input_size = os.path.getsize(input_path)
    target_size = target_info['size']

    if target_size > 0 and input_size > 0:
        ratio = min(input_size, target_size) / max(input_size, target_size)
    else:
        ratio = 0.0

    score = int(ratio * 30)
    fired = ratio >= 0.30
    evidence = f"Size ratio {ratio:.2f}"
    return score, fired, evidence


def rule2_histogram(target_info, input_path):
    try:
        import cv2
    except ImportError as e:
        return 0, False, f"OpenCV import failed: {e}"

    target_img = cv2.imread(target_info['path'])
    input_img = cv2.imread(input_path)
    if target_img is None or input_img is None:
        return 0, False, "Could not load images"

    target_hist = cv2.calcHist([target_img], [0, 1, 2], None,
                               [8, 8, 8], [0, 256, 0, 256, 0, 256])
    input_hist = cv2.calcHist([input_img], [0, 1, 2], None,
                              [8, 8, 8], [0, 256, 0, 256, 0, 256])

    cv2.normalize(target_hist, target_hist)
    cv2.normalize(input_hist, input_hist)

    similarity = cv2.compareHist(target_hist, input_hist, cv2.HISTCMP_CORREL)

    score = int(max(0, similarity) * 30)
    fired = similarity > 0.5
    evidence = f"Histogram correlation {similarity:.3f}"
    return score, fired, evidence


def rule3_template(target_info, input_path):
    try:
        import cv2
    except ImportError as e:
        return 0, False, f"OpenCV import failed: {e}"

    target_img = cv2.imread(target_info['path'])
    input_img = cv2.imread(input_path)
    if target_img is None or input_img is None:
        return 0, False, "Could not load images"

    target_gray = cv2.cvtColor(target_img, cv2.COLOR_BGR2GRAY)
    input_gray = cv2.cvtColor(input_img, cv2.COLOR_BGR2GRAY)

    th, tw = target_gray.shape[:2]
    ih, iw = input_gray.shape[:2]

    if ih <= th and iw <= tw:
        image = target_gray
        templ = input_gray
        mode = "input-in-target"
    elif th <= ih and tw <= iw:
        image = input_gray
        templ = target_gray
        mode = "target-in-input"
    else:
        return 0, False, "Incompatible sizes for template"

    if templ.shape[0] < 30 or templ.shape[1] < 30:
        return 0, False, "Template too small"

    res = cv2.matchTemplate(image, templ, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(res)

    max_val = float(max_val)
    score = int(round(max(0.0, min(1.0, max_val)) * 40))
    score = max(0, min(40, score))

    fired = max_val >= 0.55
    evidence = f"Match score {max_val:.2f} ({mode})"
    return score, fired, evidence