from src.utils.preprocess import NexusDataPreprocess

def run_test_suites(recreate_data = False):
    if recreate_data:
        NexusDataPreprocess.preprocess()
