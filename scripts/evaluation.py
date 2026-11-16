import numpy as np


def confusion_counts(y_true, y_pred):
    """0/1 마스크를 받아 TP, FP, FN, TN 순서로 반환함."""
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)

    if y_true.shape != y_pred.shape:
        raise ValueError("정답과 예측의 크기가 같아야 함.")
    if y_true.ndim != 2 or y_true.size == 0:
        raise ValueError("정답과 예측은 비어 있지 않은 2차원 배열이어야 함.")
    if not np.isin(y_true, (0, 1)).all() or not np.isin(y_pred, (0, 1)).all():
        raise ValueError("정답과 예측에는 0과 1만 있어야 함.")

    y_true = y_true == 1
    y_pred = y_pred == 1
    tp = int(np.count_nonzero(y_true & y_pred))
    fp = int(np.count_nonzero(~y_true & y_pred))
    fn = int(np.count_nonzero(y_true & ~y_pred))
    tn = int(np.count_nonzero(~y_true & ~y_pred))
    return tp, fp, fn, tn


def pixel_f1(tp, fp, fn):
    denominator = 2 * tp + fp + fn
    if denominator == 0:
        return None
    return 2 * tp / denominator


def iou(tp, fp, fn):
    denominator = tp + fp + fn
    if denominator == 0:
        return None
    return tp / denominator


def false_positive_rate(fp, tn):
    denominator = fp + tn
    if denominator == 0:
        return None
    return fp / denominator
