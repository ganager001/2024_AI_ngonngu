import json
import regex as re
import py_vncorenlp
import os
import logging

logging.basicConfig(level=logging.INFO)

class TextProcessor:
    def __init__(self):
        try:
            self.annotator = py_vncorenlp.VnCoreNLP(annotators=["wseg", "pos"], save_dir='D:\\5._CODE\\T724_Django\\mainproject\\cores\\core_model')
        except Exception as e:
            logging.error(f"Error initializing VnCoreNLP: {e}")
            raise

    def split_paragraphs(self, text):
        return text.split('\n')

    def split_sentences(self, text):
        pattern = r"""(?x)
        \S(?:
            (?:\p{Lu}|BLV|BSc|BS|BTV|Ch|CNV|CN|Dr|Gh|Gi|GS|Kh|KP|KS|KTS|KTV|MC|MSc|Mrs|Mr|Ms|NCS|NCV|Ngh|Ng|Nh|PGS|PhD|Ph|Prof|Pro|PTV|PV|Th|ThS|TP|Tr|TSKH|TS|TT|TX)\.
            |
            .
        )*?
        (?:
            (?:[:;…]|\.\.\.)(?=\s\p{Lu}|\Z|\p{Ps}|\p{Pi}|"|'|<|\||(?=\p{S}|\+|-|\||\p{Pe}|\p{Pf}|>|\.|\?|!))
            |
            [.!?](?=\s\p{Lu}|\Z|\p{Ps}|\p{Pi}|"|'|<|\||(?=\p{S}|\+|-|\||\p{Pe}|\p{Pf}|>|\.|\?|!))
            |
            (?=\n)
        )
        """
        sentences = re.findall(pattern, text, re.VERBOSE)
        return sentences if sentences else [text]

    def process_text(self, text, is_title=False):
        if is_title:
            return self.process_sentence(text)
        else:
            paragraphs = self.split_paragraphs(text)
            processed_paragraphs = []
            for paragraph in paragraphs:
                sentences = self.split_sentences(paragraph)
                processed_sentences = [self.process_sentence(sentence) for sentence in sentences]
                processed_paragraphs.append(' '.join(processed_sentences))
            return '\n'.join(processed_paragraphs)

    def process_sentence(self, sentence):
        try:
            annotation = self.annotator.annotate_text(sentence)
            if isinstance(annotation, dict):
                processed_sentence = []
                for sentence_id, sentence_data in annotation.items():
                    for token in sentence_data:
                        if isinstance(token, dict):
                            word = token.get('wordForm', '')
                            pos = token.get('posTag', '')
                            processed_sentence.append(f"{word}|{pos}")
                return " ".join(processed_sentence)
        except Exception as e:
            logging.error(f"Error processing sentence: {sentence}. Error: {e}")
            return sentence

    def process_file(self, input_file, output_file):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        input_path = os.path.join(current_dir, input_file)
        output_path = os.path.join(current_dir, output_file)

        logging.info(f"Processing file: {input_path}")
        logging.info(f"Output will be saved to: {output_path}")

        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            logging.error(f"Input file not found: {input_path}")
            return
        except json.JSONDecodeError:
            logging.error(f"Error decoding JSON from file: {input_path}")
            return

        for item in data:
            if 'title' in item:
                item['title'] = self.process_text(item['title'], is_title=True)
            for field in ['description', 'content']:
                if field in item:
                    item[field] = self.process_text(item[field])

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logging.info(f"Output saved to: {output_path}")
        except Exception as e:
            logging.error(f"Error saving output file: {e}")

if __name__ == "__main__":
    processor = TextProcessor()
    processor.process_file('../common/data_input.json', '../common/data_gan_nhan.json')
