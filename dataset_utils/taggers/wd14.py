from imgutils.tagging import get_wd14_tags
import os.path

model_name = "EVA02_Large"

def tag_image(image_path: str,
              model_name: str = model_name,
              general_threshold: float = 0.35,
              general_mcut_enabled: bool = False,
              character_threshold: float = 0.85,
              character_mcut_enabled: bool = False,
              no_underline: bool = False,
              drop_overlap: bool = False,
              fmt=('rating', 'general', 'character')):
    return get_wd14_tags(image_path, model_name, general_threshold, general_mcut_enabled, character_threshold, character_mcut_enabled, no_underline, drop_overlap, fmt)

def batch_tag_images(image_paths: list[str],
                     batch_size: int = 10,
                     model_name: str = model_name,
                     general_threshold: float = 0.35,
                     general_mcut_enabled: bool = False,
                     character_threshold: float = 0.85,
                     character_mcut_enabled: bool = False,
                     no_underline: bool = False,
                     drop_overlap: bool = False,
                     fmt=('rating', 'general', 'character')):

    from tqdm import tqdm
    from concurrent.futures import ThreadPoolExecutor, as_completed
    with ThreadPoolExecutor(max_workers=batch_size) as executor:
        futures = [executor.submit(tag_image, image_path, model_name, general_threshold, general_mcut_enabled, character_threshold, character_mcut_enabled, no_underline, drop_overlap, fmt) for image_path in image_paths]
        results = list(tqdm(as_completed(futures), total=len(futures), desc="Tagging images"))
    return results

def get_images_from_dir(dir_path: str):
    from glob import glob
    return glob(os.path.join(dir_path, '*'))

def batch_tag_images_from_dir(dir_path: str,
                              batch_size: int = 10,
                              model_name: str = model_name,
                              general_threshold: float = 0.35,
                              general_mcut_enabled: bool = False,
                              character_threshold: float = 0.85,
                              character_mcut_enabled: bool = False,
                              no_underline: bool = False,
                              drop_overlap: bool = False,
                              fmt=('rating', 'general', 'character')):
    image_paths = get_images_from_dir(dir_path)
    return batch_tag_images(image_paths, batch_size, model_name, general_threshold, general_mcut_enabled, character_threshold, character_mcut_enabled, no_underline, drop_overlap, fmt)
