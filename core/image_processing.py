import cv2
import numpy as np
from PIL import Image

def apply_image_processing(pil_img: Image.Image, params: dict) -> Image.Image:
    """
    Áp dụng các bộ lọc OpenCV lên một ảnh PIL.
    """
    # Chuyển PIL Image sang Numpy array (RGB)
    cv_img = np.array(pil_img.convert('RGB'))
    # PIL mặc định là RGB, cv2 mặc định là BGR, nhưng vì ta chủ yếu quan tâm đến Grayscale 
    # và các phép toán độ sáng/độ tương phản, nên có thể convert sang BGR trước nếu cần.
    cv_img = cv2.cvtColor(cv_img, cv2.COLOR_RGB2BGR)

    # 1. Invert Colors
    if params.get('invert', False):
        cv_img = cv2.bitwise_not(cv_img)

    # 2. Brightness and Contrast
    alpha = params.get('contrast', 1.0) # 0.1 - 3.0
    beta = params.get('brightness', 0)  # -100 - 100
    if alpha != 1.0 or beta != 0:
        cv_img = cv2.convertScaleAbs(cv_img, alpha=alpha, beta=beta)

    # 3. Grayscale
    is_gray = False
    if params.get('grayscale', False) or params.get('threshold_type', 'None') != 'None':
        cv_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
        is_gray = True

    # 4. Blur / Sharpen
    blur_kernel = int(params.get('blur_kernel', 1))
    if blur_kernel > 1 and blur_kernel % 2 == 1:
        cv_img = cv2.GaussianBlur(cv_img, (blur_kernel, blur_kernel), 0)
        
    sharpen = params.get('sharpen', False)
    if sharpen:
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        cv_img = cv2.filter2D(cv_img, -1, kernel)

    # 5. Thresholding
    thresh_type = params.get('threshold_type', 'None')
    if thresh_type == 'Simple':
        thresh_val = int(params.get('threshold_val', 127))
        _, cv_img = cv2.threshold(cv_img, thresh_val, 255, cv2.THRESH_BINARY)
    elif thresh_type == 'Adaptive':
        block_size = int(params.get('adaptive_block', 11))
        if block_size % 2 == 0:
            block_size += 1
        c_val = int(params.get('adaptive_c', 2))
        cv_img = cv2.adaptiveThreshold(cv_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, block_size, c_val)

    # 6. Morphology
    morph_type = params.get('morph_type', 'None')
    if morph_type != 'None':
        iterations = int(params.get('morph_iter', 1))
        kernel = np.ones((3, 3), np.uint8)
        if morph_type == 'Dilation':
            # Lưu ý: Trong ảnh nhị phân đen trắng (barcode), màu đen thường là đối tượng.
            # Dilation của OpenCV mở rộng viền trắng (255).
            # Để làm đậm viền nét mực đen, ta cần Erosion thay vì Dilation.
            # Ở đây ta tuân theo thuật ngữ của OpenCV:
            cv_img = cv2.dilate(cv_img, kernel, iterations=iterations)
        elif morph_type == 'Erosion':
            cv_img = cv2.erode(cv_img, kernel, iterations=iterations)
        elif morph_type == 'Open (Xóa nhiễu trắng)':
            cv_img = cv2.morphologyEx(cv_img, cv2.MORPH_OPEN, kernel, iterations=iterations)
        elif morph_type == 'Close (Nối nét đứt)':
            cv_img = cv2.morphologyEx(cv_img, cv2.MORPH_CLOSE, kernel, iterations=iterations)

    # Chuyển ngược lại sang PIL Image
    if is_gray or len(cv_img.shape) == 2:
        return Image.fromarray(cv_img).convert("RGB")
    else:
        cv_img_rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        return Image.fromarray(cv_img_rgb)
