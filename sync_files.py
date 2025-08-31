import os
import time
import logging
import hashlib
import argparse


def log_message(message):
    logging.info(message)


def get_file_hash(file_path):
    md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5.update(chunk)
    return md5.hexdigest()


def copy_file(source_file, destination_dir):
    try:
        source_hash = get_file_hash(source_file)
        source_filename = os.path.basename(source_file)
        destination_path = os.path.join(destination_dir, source_filename)
        is_duplicate = False

        # Check for duplicates in the destination folder
        for root, _, files in os.walk(destination_dir):
            for file in files:
                existing_file_path = os.path.join(root, file)
                if get_file_hash(existing_file_path) == source_hash:
                    is_duplicate = True
                    log_message(f"Duplicate file found, skipping copy: {source_file}")
                    break

        # If not a duplicate file with the same name, copy it
        if not os.path.exists(destination_path):
            with open(source_file, 'rb') as src, open(destination_path, 'wb') as dst:
                dst.write(src.read())

            if is_duplicate:
                log_message(f"'{source_filename}' added as a duplicate copy.")
            else:
                log_message(f"'{source_filename}' copied successfully.")
        else:
            log_message(f"File '{source_filename}' already exists at destination.")
    except Exception as e:
        log_message(f"Error copying file: {e}")


def copy_directory(source_path: str, replica_path: str):
    try:
        if not os.path.exists(replica_path):
            os.makedirs(replica_path)

        source_files = os.listdir(source_path)
        replica_files = os.listdir(replica_path)

        # Select files to delete
        files_to_delete = []
        for file in replica_files:
            if file not in source_files:
                files_to_delete.append(file)

        for file in files_to_delete:
            file_to_delete_path = os.path.join(replica_path, file)
            if os.path.isfile(file_to_delete_path):
                os.remove(file_to_delete_path)
                log_message(f"Deleted file: {file_to_delete_path}")
            elif os.path.isdir(file_to_delete_path):
                os.rmdir(file_to_delete_path)
                log_message(f"Deleted directory: {file_to_delete_path}")

        for item in source_files:
            source_item_path = os.path.join(source_path, item)
            replica_item_path = os.path.join(replica_path, item)

            if os.path.isdir(source_item_path):
                copy_directory(source_item_path, replica_item_path)
            else:
                copy_file(source_item_path, replica_path)
        log_message(f"Folder synced: {source_path} to {replica_path}")
    except Exception as e:
        log_message(f"Error coping directory: {e}")


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Backup tool: copy file from source to replica directory."
    )

    parser.add_argument("source_path", help="Path to the source directory")
    parser.add_argument("replica_path", help="Path to the replica directory")
    parser.add_argument("interval", type=int, help="Interval (in seconds) between synchronizations")
    parser.add_argument("amount", type=int, help="How long (in seconds) repeat the synchronization")
    parser.add_argument("log_path", help="Path to the log file")

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    source_path = args.source_path
    replica_path = args.replica_path
    interval = args.interval
    amount = args.amount
    log_path = args.log_path

    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(message)s',
        handlers=[
            logging.FileHandler(os.path.basename(log_path), mode='w'),
            logging.StreamHandler()
        ]
    )

    start_time = time.time()

    while time.time() - start_time < amount:
        try:
            copy_directory(source_path, replica_path)
        except Exception as e:
            log_message(f"Error during synchronization: {e}")
        time.sleep(interval)
