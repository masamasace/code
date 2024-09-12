from pathlib import Path
import pandas as pd
import piexif

# 緯度、経度、高度をGPSIFDのフォーマットに変換
# GPSIFDのフォーマットは、((度, 1), (分, 1), (秒, 10000))のタプル
# 例: 35.1234567 -> 35°07'24.4444'' →((35, 1), (7, 1), (244444, 10000))
def to_GPSIFD_format(value, type="lat"):
    
    if type == "lat" or type == "lon":
        temp_deg = int(value)
        temp_min = int((value - temp_deg) * 60)
        temp_sec = int(((value - temp_deg) * 60 - temp_min) * 60 * 100000)

        return ((temp_deg, 1), (temp_min, 1), (temp_sec, 100000))
    elif type == "alt":
        temp_alt = int(value)
        return (temp_alt, 1)

#### 以下の部分を変更して、csvファイルのパスと写真ファイルのディレクトリを指定してください。 ####
# csvファイルのパス
csv_path = r"3_DEM作成\240901_撮影位置情報の収集（のと里山海道）.csv"
# 写真ファイルのディレクトリ
photo_dir = r"3_DEM作成\のと里山街道周辺\Photo\1963"


# パスをPathオブジェクトに変換
csv_path = Path(csv_path).resolve()
photo_dir = Path(photo_dir).resolve()

# 結果を保存するディレクトリを作成
res_dir = Path(__file__).parent / "result"
res_dir.mkdir(exist_ok=True)

# csvファイルを読み込む
csv_data = pd.read_csv(csv_path)

# 写真ファイルのパスを取得
photo_paths = list(photo_dir.glob("*.jpg"))
photo_paths = sorted(photo_paths)

# 写真ファイルごとに処理
for photo_path in photo_paths:

    photo_name = photo_path.stem

    # photo_nameがcsv_dataのファイル名と一致する行を検索
    photo_data = csv_data[csv_data["ファイル名"] == photo_name]
    if len(photo_data) == 0:
        print(f"{photo_name} は見つかりませんでした")
        continue
    else:
        print(f"{photo_name} は見つかりました。", end=" ")

    # 緯度、経度、高度を取得して、GPSIFDのフォーマットに変換
    temp_lat = to_GPSIFD_format(photo_data["緯度"].values[0], type="lat")
    temp_lon = to_GPSIFD_format(photo_data["経度"].values[0], type="lon")
    temp_alt = to_GPSIFD_format(photo_data["高度"].values[0], type="alt")
    print("緯度", photo_data["緯度"].values[0],
          "経度", photo_data["経度"].values[0],
          "高度", photo_data["高度"].values[0])
    
    # exif情報を書き換え
    exif_dict = piexif.load(str(photo_path))
    exif_dict["GPS"][piexif.GPSIFD.GPSLatitude] = temp_lat
    exif_dict["GPS"][piexif.GPSIFD.GPSLongitude] = temp_lon
    exif_dict["GPS"][piexif.GPSIFD.GPSAltitude] = temp_alt
    exif_bytes = piexif.dump(exif_dict)
    piexif.insert(exif_bytes, str(photo_path))



