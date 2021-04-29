from GitHub import main, BASE_URL, list_branch_pull_requests
import demistomock as demisto
import json

MOCK_PARAMS = {
    'user': 'test',
    'repository': 'hello-world',
    'token': 'testtoken'
}


def load_test_data(json_path):
    with open(json_path, mode='r') as f:
        return json.load(f)


test_list_branch_pull_requests_command = load_test_data('./test_data/get-branch-pull-requests-response.json')


def test_search_code(requests_mock, mocker):
    raw_response = load_test_data('./test_data/search_code_response.json')
    requests_mock.get(f'{BASE_URL}/search/code?q=create_artifacts%2borg%3ademisto&page=0&per_page=10',
                      json=raw_response)

    mocker.patch.object(demisto, 'params', return_value=MOCK_PARAMS)
    mocker.patch.object(demisto, 'args', return_value={
        'query': 'create_artifacts+org:demisto',
        'limit': '10'
    })
    mocker.patch.object(demisto, 'command', return_value='GitHub-search-code')
    mocker.patch.object(demisto, 'results')

    main()

    results = demisto.results.call_args[0][0]
    assert results['Contents'] == raw_response
    assert len(results['EntryContext']['GitHub.CodeSearchResults(val.html_url == obj.html_url)']) == 7
    assert 'Repository Name' in results['HumanReadable']


def test_list_branch_pull_requests_command(requests_mock, mocker):
    requests_mock.get('https://api.github.com/repos/demisto/content/pulls?head=demisto:Update-Docker-Image',
                      json=test_list_branch_pull_requests_command['response'])
    results = list_branch_pull_requests(branch_name='Update-Docker-Image', repository='content', organization='demisto')
    assert results.outputs_prefix == 'GitHub.PR'
    assert results.outputs_key_field == 'Number'
    assert results.raw_response == test_list_branch_pull_requests_command['response']
    assert results.outputs == test_list_branch_pull_requests_command['expected']
