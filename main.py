import requests
from collections import defaultdict

headers = {
    "Authorization": ""
}


def fetch_repo_commits(repo_owner, repo_name):
    page = 1
    while True:
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/commits?per_page=100&page={page}"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            page += 1
            yield response
        else:
            yield None


def fetch_commit_files(repo_owner, repo_name, commit_sha):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/commits/{commit_sha}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        files = [file['filename'] for file in response.json()['files']]
        return files
    else:
        return None


def preprocess(repo_owner, repo_name, limit_commits):
    print("Starting preprocessing")
    count_commits = 0
    developer_files_counts = dict()
    developer_counts = defaultdict(lambda: [0, 0])
    file_commits = defaultdict(lambda: set())
    commits = fetch_repo_commits(repo_owner, repo_name)
    while count_commits < limit_commits:
        response = next(commits, None)
        if response is None or len(response.json()) == 0:
            print(f'The last {count_commits} commits are being considered (if this number is not equal to the number',
                  f' of commits in the repository and is less than {limit_commits}, you should repeat the request with',
                  f'another token or later)')
            return developer_files_counts, developer_counts, file_commits

        for commit in response.json():
            count_commits += 1
            if commit['author'] is None:
                continue
            contributor = commit['author']['login']

            files = fetch_commit_files(repo_owner, repo_name, commit['sha'])
            if files is None:
                print(f'The last {count_commits} commits are being considered (if this number is not equal to the',
                      f'number of commits in the repository and is less than {limit_commits}, you should repeat the',
                      f'request with another token or later)')
                return developer_files_counts, developer_counts, file_commits

            for file in files:
                file_commits[file].add(commit['sha'])
                if contributor not in developer_files_counts.keys():
                    developer_files_counts[contributor] = dict()
                if file not in developer_files_counts[contributor].keys():
                    developer_files_counts[contributor][file] = 0
                developer_files_counts[contributor][file] += 1
                developer_counts[contributor][1] += 1
            developer_counts[contributor][0] += 1
    print(f'The last {count_commits} commits are being considered (if this number is not equal to the number',
          f' of commits in the repository and is less than {limit_commits}, you should repeat the request with',
          f'another token or later)')
    return developer_files_counts, developer_counts, file_commits


def count_shared_commits(developer1, developer2, developer_files_counts, *kwargs):
    count = 0
    for file in developer_files_counts[developer1].keys():
        if file in developer_files_counts[developer2].keys():
            count += min(developer_files_counts[developer1][file], developer_files_counts[developer2][file])
    return count


def percent_shared_commits(developer1, developer2, developer_files_counts, developer_counts, *kwargs):
    shared = count_shared_commits(developer1, developer2, developer_files_counts)
    return round(shared * 100 / (developer_counts[developer1][1] + developer_counts[developer2][1] - shared), 1)


def cosine_similarity(developer1, developer2, developer_files_counts, *kwargs):
    count = 0
    developer1_square = 0
    developer2_square = 0
    for file in developer_files_counts[developer1].keys():
        developer1_square += developer_files_counts[developer1][file] ** 2
        if file in developer_files_counts[developer2].keys():
            count += developer_files_counts[developer1][file] * developer_files_counts[developer2][file]
    for file in developer_files_counts[developer2].keys():
        developer2_square += developer_files_counts[developer2][file] ** 2
    return round(count / ((developer1_square * developer2_square) ** 0.5), 2)


def search_pairs(developer_files_counts, developer_counts, ignore_number, answers_number, metric):
    pairs = defaultdict(int)
    sign = {count_shared_commits: '', percent_shared_commits: '%', cosine_similarity: ''}

    for developer1 in developer_files_counts.keys():
        if developer_counts[developer1][0] <= ignore_number:
            continue
        for developer2 in developer_files_counts.keys():
            if developer_counts[developer2][0] <= ignore_number:
                continue
            if developer1 < developer2:
                pairs[(developer1, developer2)] = metric(developer1, developer2, developer_files_counts,
                                                         developer_counts)

    sorted_pairs = sorted(pairs.items(), key=lambda x: x[1], reverse=True)
    for pair, count in sorted_pairs[:answers_number]:
        print(f'{pair[0]} and {pair[1]} have {count}{sign[metric]} similar commits')


def search_files(file_commits, answers_number):
    pairs = dict()
    for file1 in file_commits.keys():
        for file2 in file_commits.keys():
            if file1 < file2:
                intersection = len(file_commits[file1].intersection(file_commits[file2]))
                pairs[(file1, file2)] = intersection * 100 / (
                            len(file_commits[file1]) + len(file_commits[file2]) - intersection)

    sorted_pairs = sorted(pairs.items(), key=lambda x: x[1], reverse=True)
    for pair, count in sorted_pairs[:answers_number]:
        print(f'{pair[0]} and {pair[1]} have {count}% similar commits')


def greetings():
    print('''Hello, I can calculate some useful metrics for the provided GitHub repository. I can calculate following metrics:
    - First option: The most related pairs by the number of changes to the same files
    - Second option: The most related pairs by the percentage of changes to the same files
    - Third option: The most related pairs by the Cosine similarity''')


def helper():
    print('''Enter what type of operation to perform:
    "1 number_of_pairs" to calculate number_of_pairs most related pairs of contributors for current repository in absolute metric
    "2 number_of_pairs" to calculate number_of_pairs most related pairs of contributors for current repository in percentage metric
    "3 number_of_pairs" to calculate number_of_pairs most related pairs of contributors for current repository in Cosine similarity
    "4 number_of_pairs" to calculate number_of_pairs most related pairs of files for current repository in percentage metric
    "5 new_ignore_number" to change the ignore_number developers with this number of commits or less are not counted in the search (default is 1)
    "6 new_count_commits" to change the number of recent commits under consideration (it cannot be more than 4950, and also with a large number, the waiting time can be very long)
    "7 new_repo_owner new_repo_name" to change repo_owner and repo_name to new_repo_owner and new_repo_name
    "help" to see this message
    "exit" to exit the program\n''')


def main():
    global headers
    greetings()
    repo_owner = input("Enter the repository owner:").strip()
    repo_name = input("Enter the repository name:").strip()
    ignore_number = 1
    limit_commits = 1000
    token = input("Enter personal access token for REST API:")
    headers = {"Authorization": f"token {token}"}
    developer_files_counts, developer_counts, file_commits = preprocess(repo_owner, repo_name, limit_commits)
    helper()
    while True:
        input_string = input().split()
        if len(input_string) == 0:
            print("Invalid operation type")
            continue
        operation_type = input_string[0]
        if operation_type.isnumeric() and int(operation_type) < 4:
            number_of_strings = int(input_string[1])
            metrics = [count_shared_commits, percent_shared_commits, cosine_similarity]
            search_pairs(developer_files_counts, developer_counts, ignore_number, number_of_strings,
                         metrics[int(operation_type) - 1])
        elif operation_type == "4":
            number_of_strings = int(input_string[1])
            search_files(file_commits, number_of_strings)
        elif operation_type == "5":
            ignore_number = int(input_string[1])
        elif operation_type == "6":
            limit_commits = int(input_string[1])
            developer_files_counts, developer_counts, file_commits = preprocess(repo_owner, repo_name, limit_commits)
        elif operation_type == "7":
            repo_owner = input_string[1]
            repo_name = input_string[2]
            developer_files_counts, developer_counts, file_commits = preprocess(repo_owner, repo_name, limit_commits)
        elif operation_type == "help":
            helper()
        elif operation_type == "exit":
            exit()
        else:
            print("Invalid operation type")


if __name__ == "__main__":
    main()
