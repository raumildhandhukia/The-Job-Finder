import fetch_data as fetch
import dump_to_csv as dump

if __name__ == '__main__':
    fetch.fetch_jobs()
    dump.dump_to_csv()
