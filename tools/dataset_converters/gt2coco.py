import argparse
import json
import os

def convert_to_coco(ann_folder_path, outfile):
    ''' ann_file은 via_region_data.json, out_file은 coco로 변환할 출력 json파일
        image_prefix는 image jpg가 있는 디렉토리 위치 
    '''

    # 클래스 정보 (후에 클래스 정보 바뀌면 이거랑 밑에 있는 categroy 업데이트 해야됨.)
    category_class = {"vehicle":0,"walker":1,'trafficlight':2,"roadsign":3}
    # 모든 obj에 대해 번호 하나씩 달꺼임. 별 의미는 없음.
    obj_count = 0

    # coco format (개별 이미지에 대해, obj별 annotations에 대해, 그리고 카테고리 정보들.)
    coco_format_json = dict(
        images = [],
        annotations = [],
        categories = []
    )
    images = []
    annotations = []
    
    # 폴더 안에서 json 파일 다 열어볼 것
    json_file_names = os.listdir(ann_folder_path)
    for file_name in json_file_names:
        ann_file = ann_folder_path + file_name

        # 각각의 json 파일 가져오기.
        with open(ann_file) as json_file:
            data_info = json.load(json_file)

        # 개별 이미지들에 대해서 저장 (각각의 json 파일은 곧 각각의 이미지 파일에 대한 정보를 포함)
        images.append(dict(
            id = int(data_info['gt_data']['camera_data']['name'][:-8]),
            file_name = data_info['gt_data']['camera_data']['name'],
            height = data_info['gt_data']['camera_data']['size']['height'],
            width = data_info['gt_data']['camera_data']['size']['width']
        ))
        # print(f'image append! {obj_count}')

        #bbox와 polygon
        bboxes_info = data_info['gt_data']['label_data']['2d_bounding_box']
        polygon_info = data_info['gt_data']['label_data']['polygon']
        
        # 각 obj에 대해
        idx = 0     # bbox는 출력되는데 polygon이 출력 안되는 경우가 있어서 이렇게 함.
        for bbox in bboxes_info:
            
            # occluded, truncated 설정
            # if bbox['truncated'] != 0 or bbox['occluded'] != 0 :
            #     continue

            # boundingbox
            left = bbox['left']['top']['x']
            top = bbox['left']['top']['y']
            width = bbox['right']['bottom']['x'] - left
            height = top - bbox['right']['bottom']['y']
            
            # polygon_area
            # if polygon_info[idx]['area'] < 60 :
            #     continue

            # bbox는 출력되는데 polygon이 출력 안되는 경우가 있어서 다음 코드를 추가함.
            if bbox['id'] != polygon_info[idx]['id'] :
                idx -= 1
                continue

            # polygon이 하나의 객체에 대해 여러 개 인 경우
            for plist in polygon_info[idx]['point_list'] :
                polygon = [p for point in plist for p in point.values()]


                # 객체별로(엄밀히 말해, 객체 안의 polygon 별로) annotation 생성
                data_anno = dict(
                    image_id = int(data_info['gt_data']['camera_data']['name'][:-8]),
                    id = obj_count,
                    category_id = category_class[bbox['class']['level1']],
                    bbox = [int(left),int(top),int(width),int(height)],
                    area = width*height,
                    segmentation = [polygon],
                    iscrowd = 0
                )
                annotations.append(data_anno)
                obj_count +=1

            idx += 1

    coco_format_json['images'] = images 
    coco_format_json['annotations'] = annotations 
    coco_format_json['categories'] = [{'id':0, 'name':'vehicle'},{'id':1, 'name':'walker'},
                                    {'id':2, 'name':'trafficlight'}, {'id':3, 'roadsign':3}]
    with open(outfile,'w') as json_out_file:
        json.dump(coco_format_json, json_out_file)


def parse_args():
    parser = argparse.ArgumentParser( description = " ann_file은 via_region_data.json, out_file은 coco로 변환할 출력 json파일, image_prefix는 image jpg가 있는 디렉토리 위치 ")
    parser.add_argument('-a', '--ann_folder_path', help='ann_folder_path')
    parser.add_argument('-o', '--outfile', help='outfile')
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    ann_folder_path, outfile = args.ann_folder_path, args.outfile
    convert_to_coco(ann_folder_path, outfile)
    

if __name__ == '__main__':
    main()
