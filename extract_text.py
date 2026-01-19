import olefile
import zlib
import struct
import os

def get_text(file_path):
    if not olefile.isOleFile(file_path):
        return None

    try:
        f = olefile.OleFileIO(file_path)
        # HWP 본문 텍스트는 BodyText 하위의 Section들에 저장됩니다.
        dirs = f.listdir()
        sections = [d for d in dirs if d[0] == 'BodyText' and d[1].startswith('Section')]
        sections.sort() # Section0, Section1... 순서대로 정렬

        full_text = []

        for section in sections:
            stream = f.openstream(section)
            data = stream.read()
            
            # 압축 해제 (HWP는 문서 정보를 제외한 본문은 보통 압축되어 있음)
            try:
                # zlib 압축 해제 (-15는 Raw Deflate 헤더 무시)
                decompressed = zlib.decompress(data, -15)
            except:
                decompressed = data

            # 레코드 구조 해석하여 텍스트만 추출
            i = 0
            while i < len(decompressed):
                # 4바이트 레코드 헤더 읽기
                header = struct.unpack('<I', decompressed[i:i+4])[0]
                tag_id = header & 0x3FF
                length = (header >> 20) & 0xFFF
                
                # Tag ID 67이 본문 텍스트(HWPTAG_PARA_TEXT)입니다.
                if tag_id == 67:
                    content = decompressed[i+4 : i+4+length]
                    # UTF-16으로 디코딩 (한글 본문은 유니코드)
                    full_text.append(content.decode('utf-16', errors='ignore'))
                
                # 다음 레코드로 이동 (헤더 4바이트 + 데이터 길이)
                i += 4 + length

        return "\n".join(full_text)

    except Exception as e:
        # return f"추출 중 오류 발생: {e}"
        return None
