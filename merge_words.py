import pandas as pd
import glob

def merge_word_files():
    # 自動搜尋所有 level 檔案 (包含 level 1 到 level 6)
    all_files = glob.glob("words_level*.csv")
    
    if not all_files:
        print("沒有找到任何 words_level*.csv 檔案！")
        return

    df_list = []
    for filename in sorted(all_files):
        try:
            temp_df = pd.read_csv(filename)
            print(f"成功讀取: {filename}，共 {len(temp_df)} 筆資料")
            df_list.append(temp_df)
        except Exception as e:
            print(f"讀取 {filename} 失敗: {e}")

    if df_list:
        # 合併所有 DataFrame
        combined_df = pd.concat(df_list, ignore_index=True)
        
        # 去除重複的單字 (以 word 欄位為主)
        if "word" in combined_df.columns:
            combined_df = combined_df.drop_duplicates(subset=["word"])
        
        # 將 level 轉換為數字並由小到大排序 (Level 1 排在最前面)
        if "level" in combined_df.columns:
            combined_df["level"] = pd.to_numeric(combined_df["level"], errors="coerce")
            combined_df = combined_df.sort_values(by="level", ascending=True)
            
        combined_df = combined_df.reset_index(drop=True)
        
        # 覆蓋或儲存成最新的 words.csv 總表
        combined_df.to_csv("words.csv", index=False, encoding="utf-8-sig")
        print(f"大合併完成！已成功更新 words.csv，總計 {len(combined_df)} 筆不重複單字。")

if __name__ == "__main__":
    merge_word_files()
