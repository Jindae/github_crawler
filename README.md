# GitHub Public Data Crawler

A Public Data Crawler for GitHub using GitHub REST API.   

Currently, it is a sample implement to collect issues and store them to MongoDB.   
The implementation reads `sample_repositories.csv`, and use the repository information to collect issues.   
You can modify `parseResponse()`, `getURL()` functions as you want, based on the data you need to collect. 
The information you can collect from GitHub REST API can be found in [here](https://docs.github.com/en/rest).

In order to execute, you need to register your GitHub Username and Personal Access Token(PAT) for authentication.   
If you register multiple authentication information, the crawler automatically rotate the authentication info. within Rate Limit to collect data.   
In order to create PAT, you can check [here](https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token).  

During crawling, you can check registered users' rate limit by running `rate_limit_info.py`.

------------------------------------------------

GitHub REST API를 이용하여 정보를 수집하는 Crawler입니다.   

현재는 `sample_repositories.csv`의 repository 정보를 읽어 이슈들을 수집하고, MongoDB에 저장하는 예제로 구현이 되어있습니다.   
수집하고자 하는 데이터에 맞게 `parseResponse()`, `getURL()` 등의 함수를 수정하여 사용하시면 됩니다.    
GitHub REST API로 얻을 수 있는 정보에 대한 자세한 내용은 [여기](https://docs.github.com/en/rest)를 참조하세요.
   
실행을 위해서 `settings.json`에 GitHub Username과 Personal Access Token(PAT)를 등록해주면,    
Crawler가 Rate Limit 한도 내에서 자동으로 등록된 사용자를 번갈아 사용하여 정보를 수집합니다.   
PAT을 생성하는 방법은 [여기](https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token)를 참조하세요.  

Crawling을 하는 도중 `rate_limit_info.py`를 실행하면 등록해 놓은 사용자들의 Rate Limit과 관련된 정보를 확인할 수 있습니다. 
