from dataclasses import dataclass

from src.loader import Document


@dataclass
class Chunk:
    text: str
    metadata: dict


def _is_table_line(line: str) -> bool:
    """Markdownの表行（| で始まる行）かどうかを判定する。"""
    stripped = line.strip()
    return stripped.startswith("|") and stripped.endswith("|")


def _extract_blocks(text: str) -> list[tuple[str, str]]:
    """テキストを「表ブロック」と「通常テキストブロック」のリストに分解する。

    各要素は (block_type, content) のタプル。block_type は "table" または "text"。
    表の前後に表に関連するセクション見出しがあればそれも表ブロックに含める。
    """
    lines = text.split("\n")
    blocks: list[tuple[str, str]] = []
    current_text_lines: list[str] = []
    i = 0

    while i < len(lines):
        line = lines[i]

        if _is_table_line(line):
            # 表の開始を検出。表の直前の見出し行（##で始まる行）を探す
            preceding_header = []
            if current_text_lines:
                # 末尾の空行をスキップ
                end_idx = len(current_text_lines)
                while end_idx > 0 and current_text_lines[end_idx - 1].strip() == "":
                    end_idx -= 1

                # その手前から、次の空行までを取得
                start_idx = end_idx
                while start_idx > 0 and current_text_lines[start_idx - 1].strip() != "":
                    start_idx -= 1

                candidate = current_text_lines[start_idx:end_idx]
                # 候補に見出し行が含まれているか確認
                if candidate and any(line.lstrip().startswith("#") for line in candidate):
                    preceding_header = candidate
                    # current_text_lines から取り除く
                    current_text_lines = current_text_lines[:start_idx]

            # ここまでの通常テキストをブロック化
            if current_text_lines:
                text_content = "\n".join(current_text_lines).strip()
                if text_content:
                    blocks.append(("text", text_content))
                current_text_lines = []

            # 表の連続行を全て収集
            table_lines = list(preceding_header)
            while i < len(lines) and (_is_table_line(lines[i]) or lines[i].strip() == ""):
                # 表の途中の空行は表の終わりとみなす
                if lines[i].strip() == "":
                    # 次の行も表行ならば空行を含めて続行、そうでなければ終了
                    if i + 1 < len(lines) and _is_table_line(lines[i + 1]):
                        table_lines.append(lines[i])
                        i += 1
                        continue
                    break
                table_lines.append(lines[i])
                i += 1

            blocks.append(("table", "\n".join(table_lines)))
        else:
            current_text_lines.append(line)
            i += 1

    if current_text_lines:
        text_content = "\n".join(current_text_lines).strip()
        if text_content:
            blocks.append(("text", text_content))

    return blocks


def _split_text_block(text: str, chunk_size: int, overlap: int) -> list[str]:
    """通常テキストを文字数ベースで分割する。"""
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks


def split_text(document: Document, chunk_size: int = 500, overlap: int = 100) -> list[Chunk]:
    """ドキュメントをチャンクに分割する。

    v7: 表認識チャンキング
    - Markdownの表は分割せず、表全体を1つのチャンクとして保持する
    - 通常テキストは従来通り chunk_size で分割する
    """
    text = document.content
    if not text:
        return []

    blocks = _extract_blocks(text)
    chunks: list[Chunk] = []
    index = 0

    for block_type, content in blocks:
        if block_type == "table":
            # 表は分割せず1チャンクに
            chunks.append(Chunk(
                text=content,
                metadata={
                    "source_url": document.url,
                    "chunk_index": index,
                    "block_type": "table",
                },
            ))
            index += 1
        else:
            # 通常テキストは従来通り分割
            for piece in _split_text_block(content, chunk_size, overlap):
                chunks.append(Chunk(
                    text=piece,
                    metadata={
                        "source_url": document.url,
                        "chunk_index": index,
                        "block_type": "text",
                    },
                ))
                index += 1

    return chunks
