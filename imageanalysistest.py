import cv2
import face_recognition
import mediapipe as mp
import numpy as np
import math
from colorAnalysis import get_top_dominant_color, extract_dominant_colors

height = width = 0
def analyze_image(mainfile, relativefile):
    image1 = face_recognition.load_image_file(mainfile)
    image2 = face_recognition.load_image_file(relativefile)

    face_encoding1 = face_recognition.face_encodings(image1)[0]
    face_encoding2 = face_recognition.face_encodings(image2)[0]

    # Compare the faces
    distance = face_recognition.face_distance([face_encoding1], face_encoding2)
    imageDetails = granalysis(mainfile, relativefile)

    cv2.imwrite('static/files/j.png', imageDetails[0][5])
    #cv2.imwrite(relativefile, imageDetails[1][5])

    imageDiffs = []
    labels = []
    for (val1, label1), (val2, label2) in zip(imageDetails[0][:5], imageDetails[1][:5]):
        print(abs(val1-val2), label1)
        imageDiffs.append(2-10*(abs(val1-val2)))
        labels.append(label1)
    simscore = ((x := sum(imageDiffs) * 2) + (y:=(1-(distance/1.5))*80))/100

    if simscore>0.65:
        simscore = (1-simscore)/2+simscore
    if simscore<0.5:
        simscore = simscore/1.5
    print(simscore)

    min1idx = imageDiffs.index(min(imageDiffs))
    min2idx = imageDiffs.index(min(imageDiffs[:min1idx] + imageDiffs[min1idx+1:]))
    maxIdx = imageDiffs.index(max(imageDiffs))

    meye, mskin, mlip = imageDetails[0][6:]
    reye, rskin, rlip = imageDetails[1][6:]

    cv2.imwrite('static/files/meye.png', meye)
    cv2.imwrite('static/files/mskin.png', mskin)
    #cv2.imwrite('static/files/mlip.png', mlip)
    cv2.imwrite('static/files/reye.png', reye)
    cv2.imwrite('static/files/rskin.png', rskin)
    #cv2.imwrite('static/files/rlip.png', rlip)

    eyeDist, eye1, eye2 = canalysis(meye, reye)
    skinDist, skin1, skin2 = canalysis(mskin, rskin)
    lipDist, lip1, lip2 = (0,0,0)#canalysis(mlip, rlip)


    analysisDict = {
        "score": str(round(simscore[0]*100, 2)) + "%",
        "distances": imageDiffs,
        'labels': labels,
        'filepath': '/static/files/j.png',
        'relativefilepath': relativefile,
        'min1': labels[min1idx],
        'min2': labels[min2idx],
        'max': labels[maxIdx],
        'eyeDist': round(eyeDist, 2),
        'skinDist': round(skinDist, 2),
        'lipDist': lipDist,
        'eye1': eye1,
        'eye2': eye2,
        'skin1': skin1,
        'skin2': skin2,
        'lip1': lip1,
        'lip2': lip2



    }

    return analysisDict
def resizeImg(img, scale_percent=0, dims = (0,0)):
    # percent of original size
    if scale_percent:
        width = int(img.shape[1] * scale_percent / 100)
        height = int(img.shape[0] * scale_percent / 100)
        dim = (width, height)

        return cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
    else:
        return cv2.resize(img, dims, interpolation=cv2.INTER_AREA)
def dist(i1, i2, face_landmarks, img, idx=0, printline = False):

    colors = [
        (255, 0, 0),
        (0, 255, 0),
        (0, 0, 255),
        (0, 0, 0)

    ]
    l1 = face_landmarks.landmark[i1]
    l2 = face_landmarks.landmark[i2]

    l1x = int(l1.x * width)
    l1y = int(l1.y * height)

    l2x = int(l2.x * width)
    l2y = int(l2.y * height)
    if printline:
        cv2.line(img, (l1x, l1y), (l2x, l2y), colors[idx % len(colors)], 10)

    return ((l1x, l1y), (l2x, l2y), np.sqrt((l2x - l1x) ** 2 + (l2y - l1y) ** 2))
def depthdist(i1, i2, i3, face_landmarks, img):
    if i3==-1:
        i3 - i1
    l1 = face_landmarks.landmark[i1]
    l2 = face_landmarks.landmark[i2]
    l3 = face_landmarks.landmark[i3]



    return ((l1.z + l3.z)/2)-l2.z
def granalysis(filename, relativefilename):
    global width, height
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    mp_face_mesh = mp.solutions.face_mesh
    drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)

    IMAGE_FILES = [filename, relativefilename]
    imageComparison = []
    for filename in IMAGE_FILES:
        with mp_face_mesh.FaceMesh(
                static_image_mode=True,
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.5) as face_mesh:



            image = cv2.imread(filename)
            # Convert the BGR image to RGB before processing.
            results = face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

            # Print and draw face mesh landmarks on the image.
            if not results.multi_face_landmarks:
                print('broken')

            annotated_image = image.copy()

            for id, face_landmarks in enumerate(results.multi_face_landmarks):

                # facial area selection

                mp_drawing.draw_landmarks(
                    image=annotated_image,
                    landmark_list=face_landmarks,
                    connections=mp_face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=mp_drawing_styles
                    .get_default_face_mesh_tesselation_style())
                mp_drawing.draw_landmarks(
                    image=annotated_image,
                    landmark_list=face_landmarks,
                    connections=mp_face_mesh.FACEMESH_CONTOURS,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=mp_drawing_styles
                    .get_default_face_mesh_contours_style())
                mp_drawing.draw_landmarks(
                    image=annotated_image,
                    landmark_list=face_landmarks,
                    connections=mp_face_mesh.FACEMESH_IRISES,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=mp_drawing_styles
                    .get_default_face_mesh_iris_connections_style())

                height, width, _ = annotated_image.shape
                # print(f'face_landmarks: {face_landmarks}')

                eyeList = [
                    (475, 476), (474, 475), (477, 474), (476, 477),  # right
                    (472, 469), (471, 472), (469, 470), (470, 471)  # left
                ]

                skinSector = [3, 281]
                lipSector = [86, 315]

                # surround right eye

                xs = []
                ys = []
                # for idx in [472, 469, 471, 470]:
                for idx in [474, 475, 476, 477]:
                    l1 = face_landmarks.landmark[idx]
                    xs.append(int(l1.x * width))
                    ys.append(int(l1.y * height))

                eye_xtop = min(xs)
                eye_xbottom = max(xs)
                eye_ytop = min(ys)
                eye_ybottom = max(ys)

                ((skin_xtop, skin_ytop), (skin_xbottom, skin_ybottom), distance) = dist(skinSector[0], skinSector[1],
                                                                                        face_landmarks, annotated_image)

                # lip sector
                ((lip_xtop, lip_ytop), (lip_xbottom, lip_ybottom), distance) = dist(lipSector[0], lipSector[1],
                                                                                    face_landmarks, annotated_image)
                croppedEye = image[eye_ytop:eye_ybottom, eye_xtop:eye_xbottom]
                croppedSkin = image[skin_ytop:skin_ybottom, skin_xtop:skin_xbottom]
                croppedLip = image[lip_ytop:lip_ybottom, lip_xtop:lip_xbottom]

                nlfl = dist(1, 168, face_landmarks, annotated_image)[2] / dist(10, 152, face_landmarks, annotated_image)[2]
                nwnl = dist(102, 331, face_landmarks, annotated_image)[2] / dist(1, 168, face_landmarks, annotated_image)[2]
                mhw = dist(0, 17, face_landmarks, annotated_image)[2] / dist(61, 291, face_landmarks, annotated_image)[2]
                rehw = dist(386, 374, face_landmarks, annotated_image)[2] / dist(362, 263, face_landmarks, annotated_image)[
                    2]
                lehw = dist(159, 145, face_landmarks, annotated_image)[2] / dist(33, 133, face_landmarks, annotated_image)[
                    2]
                ehw = (rehw + lehw) / 2
                res = dist(362, 133, face_landmarks, annotated_image)[2] / dist(33, 263, face_landmarks, annotated_image)[2]
                depth = depthdist(393, 164, 167, face_landmarks, annotated_image)

                imageComparison.append(((nlfl, "external nose proportions"),
                                        (nwnl, "nose height and width proportions"),
                                        (mhw, "mouth height and width proportions"),
                                        (ehw, "eye height and width proportions"),
                                        (res, "eye interocular distances"),
                                        annotated_image, croppedEye, croppedSkin, croppedLip))

    return imageComparison
def main(img1, img2):
    image1 = face_recognition.load_image_file(img1)
    image2 = face_recognition.load_image_file(img2)

    # Get the face encodings for each face
    face_encoding1 = face_recognition.face_encodings(image1)[0]
    face_encoding2 = face_recognition.face_encodings(image2)[0]

    # Compare the faces
    results = face_recognition.face_distance([face_encoding1], face_encoding2)

    # Print the similarity score
    print(results)
    if results[0] == True:
        print("The two faces are a match!")
    else:
        print("The two faces do not match.")

def canalysis(img1, img2):
    manalysis = get_top_dominant_color(extract_dominant_colors(img1))
    ranalysis = get_top_dominant_color(extract_dominant_colors(img2))
    return (math.sqrt(sum([(i-j)**2 for i, j in zip(manalysis[0], ranalysis[0])])), manalysis[0], ranalysis[0])

if __name__ == '__main__':
    analysis = analyze_image('static/files/ch1.png', 'static/files/ch1.png')
    score = analysis['score']
    imageDetails = analysis['distances']

    print(score)
    print()
    for val in imageDetails:
        print(val)
    print(sum(imageDetails))


