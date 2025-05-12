from PIL import Image
import sys
import json
import os
import re

# 再帰的検索
def find_key(data):
    results={}
    
    def search(obj):
        if isinstance(obj, dict):

            for key, value in obj.items():

                # Check if the key "seed" exists in the dictionary
                if key == "seed":
                    # seedであれば、stepsも存在するであろうという決め打ち
                    steps_value = obj.get("steps")
                    cfg_value = obj.get("cfg")
                    sampler_name_value = obj.get("sampler_name")
                    scheduler_value = obj.get("scheduler")
                    denoise_value = obj.get("denoise")
                    if steps_value != None:
                        results[key]=value
                        results["cfg"]=cfg_value
                        results["sampler_name"]=sampler_name_value
                        results["scheduler"]=scheduler_value
                        results["denoise"]=denoise_value

                # Check if the key "ckpt_name" exists in the dictionary
                if key =="ckpt_name":
                    results[key]=value

                # Check if the key "width" exists in the dictionary
                if key =="width":
                    height_value = obj.get("height")
                    if height_value != None:
                        results[key]=value
                        results["height"]=height_value

                # Check if the key "lora_name" exists in the dictionary
                if key == "lora_name":
                    strength_model_value = obj.get("strength_model")
                    strength_clip_value = obj.get("strength_clip")
                    if strength_model_value != None:
                        results[key]=value
                        results["strength_model"]="{:.2f}".format(strength_model_value)
                        results["strength_clip"]="{:.2f}".format(strength_clip_value)

                search(value)
        elif isinstance(obj, list):
            for item in obj:
                search(item)
    
    search(data)
    # Check if the key "text" exists in the dictionary
    prompt_value, negative_prompt_value=find_prompt_value(data)
    results["prompt"]=prompt_value
    results["negative_prompt"]=negative_prompt_value

    return results

# promptとnegative_promptの値を抽出
def find_prompt_value(data):
    text_list_positive = []
    text_list_negative = []

    def search(node_id, mode):
        """ 指定されたノードIDから再帰的にテキストを探索 """
        # print(node_id)
        if node_id in data:
            obj = data[node_id]["inputs"]

            # textを発見したら適切なリストへ追加
            if "text" in obj:
                if isinstance(obj["text"], str):  # 直接テキストなら追加
                    if mode == "positive":
                        text_list_positive.append(obj["text"])
                    elif mode == "negative":
                        text_list_negative.append(obj["text"])
                elif isinstance(obj["text"], list):  # リストなら番号を探索
                    search(obj["text"][0], mode)

            # conditioning_to を探索
            if "conditioning_to" in obj:
                search(obj["conditioning_to"][0], mode)  # 再帰的に探索

            # conditioning_from を探索
            if "conditioning_from" in obj:
                search(obj["conditioning_from"][0], mode)  # 再帰的に探索

    # positive & negative を探索する
    for key in data:
        if "positive" in data[key]["inputs"]:
            search(data[key]["inputs"]["positive"][0], "positive")  # positiveを探索
        if "negative" in data[key]["inputs"]:
            search(data[key]["inputs"]["negative"][0], "negative")  # negativeを探索

    #print(f"text_list_positive->{text_list_positive}")
    #print(f"text_list_negative->{text_list_negative}")

    # , で区切ると丁度いいかもしれない
    final_positive_text = ",".join(text_list_positive)
    final_negative_text = ",".join(text_list_negative)

    # Dynamic Promptなど、プロンプトを改行を表示するときにアンコメントする
    #final_positive_text=final_positive_text.replace("\n", "<br>")
    
    final_positive_text=final_positive_text.replace("\n", "")
    final_positive_text = re.sub(r" {2,}", "", final_positive_text)

    # Dynamic Promptなど、プロンプトを改行を表示するときにアンコメントする
    #final_negative_text=final_negative_text.replace("\n", "<br>")

    final_negative_text=final_negative_text.replace("\n", "")
    final_negative_text = re.sub(r" {2,}", "", final_negative_text)

    #print(f"final_positive_text->{final_positive_text}")
    #print(f"final_negative_text->{final_negative_text}")

    return final_positive_text, final_negative_text


def read_png_metadata(filepath):
    try:
        # 画像ファイルを開く
        with Image.open(filepath) as img:
            # PNG画像の情報を取得 (info属性にメタデータが含まれる)
            metadata = img.info

            print(f"ファイル: {filepath}")
            print("PNGメタデータ (img.info):")
            if metadata:

                for key, value in metadata.items():
                    # metadataにはpromptとworkflowがあり                    
                    if key == "prompt":
                    
                        json_string=value
                        json_data=json.loads(json_string)
                        result=find_key(json_data)
                    else:
                        pass
            else:
                print("メタデータが見つかりませんでした。")
        
        return result

    except FileNotFoundError:
        print(f"エラー: ファイル '{filepath}' が見つかりません。", file=sys.stderr)
    except Exception as e:
        print(f"エラー: ファイルの読み込み中に問題が発生しました: {e}", file=sys.stderr)

def html_create(filepaths, results):

    # https://docs.python.org/ja/3.6/library/string.html#format-string-syntax
    html_template = """\
    <!DOCTYPE html>
    <html lang="ja">

    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ComfyUI-Image-Log</title>
        <style>
            .container {{
                display: flex;
                width: 100%;
                max-width: 1920px;/*1920や1280で広がる*/
                margin: 20px auto;
                border: 1px solid #ccc;
                padding: 10px;
            }}
            .image-box {{
                flex: 1;
                text-align: center;
            }}
            .metadata-box {{
                flex: 1;
                padding-left: 20px;
                font-family:  "Yu Gothic",Arial, sans-serif;
                /* 5/11 追加 */
                font-size: 20px;
            }}
            img {{
                /* 5/11 追加 */
                max-width: 768px;
                /*max-width: 100%;*/
                height: auto;
                border: 1px solid #ddd;
            }}
            h1{{
                text-align: center;
            }}
        </style>
    </head>

    <body>
        <h1>ComfyUI-Image-Log</h1>
            {content}
        </div>
    </body>

    </html>
    """

    # templateの表示
    # print(html_template)

    # メタデータを動的に埋め込む
    metadata_html = ""

    # 修正後
    content_html=""
    for filepath, metadata in zip(filepaths, results):
        metadata_html = ""
        for key, value in metadata.items():
            metadata_html += f'<strong>{key}:</strong> {value}<br>\n'

        content_html += f"""\
        <div class="container">
            <div class="image-box">
                <img src="{filepath}" alt="生成画像">
            </div>
            <div class="metadata-box">
                <!--<h2>画像情報</h2>-->
                {metadata_html}
            </div>
        </div>
        """

    # メタデータの表示
    #print(metadata_html)

    # HTMLに変換
    html_output=html_template.format(content=content_html)
    
    # htmlの表示
    # print(html_output)

    return html_output

# 指定したフォルダ内のPNG画像のリストを取得
def get_png_files(directory):
    return [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.png')]

def main():
    # ドラッグ＆ドロップされたパスを取得
    if len(sys.argv) > 1:
        folder_path = sys.argv[1]  # ドロップされたファイル/フォルダのパス
        print(f"フォルダのパス: {folder_path}")

        # フォルダ内のファイル一覧を取得
        if os.path.isdir(folder_path):
            
            # 実際のフォルダパスに変更
            # image_directory = "."  
            image_directory = folder_path
            png_files = get_png_files(image_directory)

            results = [read_png_metadata(f) for f in png_files]

            html_content = html_create(png_files, results)

            # HTMLファイルとして保存
            output_filename = "ComfyUI-Image-Log.html"
            with open(os.path.join(folder_path,output_filename), "w", encoding="utf-8") as f:
                f.write(html_content)

            print(f"HTMLファイルを作成しました: {output_filename}")

        else:
            print("これはフォルダではありません。")

    else:
        print("フォルダをドラッグ＆ドロップしてください。")

if __name__ == "__main__":
    main()