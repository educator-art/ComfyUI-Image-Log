# ComfyUI-Image-Log

## 概要
[ComfyUI](https://github.com/comfyanonymous/ComfyUI)で出力した画像のpnginfoを抽出します。
その後、生成した画像とプロンプト情報を一括して見るHTMLを出力することができます。
このプログラムはスタンドアロンで動作しますので、GPUを所持していないComfyUIを使うColabユーザーに向けて作られています。ローカルPCで実行することができます。
このプログラムは、[Fooocus](https://github.com/lllyasviel/Fooocus)の"log.html"に影響を受けました。

## 前提

- Windows 11
    - [Python](https://www.python.org/) 
        - [Pillow](https://github.com/python-pillow/Pillow)
        - [Nuitka](https://nuitka.net/) (Optional)

> [!NOTE]
> Macは動作の確認をしていません

> [!NOTE]
> NuitkaでPythonのスクリプトを実行形式(exe)にビルドするときには、別途、Python 3.11のインストールが必要です。

## 導入方法

```
# プロジェクトをクローンする
git clone https://github.com/educator-art/ComfyUI-Image-Log

cd ComfyUI-Image-Log

# 仮想環境の作成をする
py -3.11 -m venv build_env 
build_env\Scripts\activate

# Python 3.11であるか確認する
python --version  

#pillowとnuitkaをインストールする
pip install pillow
pip install nuitka

# 仮想環境内のパッケージ一覧を確認する
pip list          
```

> [!NOTE]
> py -3.11はNuitkaで実行形式（exe）にビルドするために使いますが、Pythonでスクリプトを実行するだけであれば、"py -3.11"を"python"に置き換えてよいです。逆に、実行形式にするとフォルダをexeにドラックアンドドロップしたときに、自動的にフォルダの中にHTMLが出来上がるので便利です。Pythonを実行するコマンドの入力が不要になります。

### ビルドする方法

```
python -m　nuitka --onefile --standalone ComfyUI-Image-Log.py
```
