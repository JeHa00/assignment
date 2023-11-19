# 중점사항

- 주어진 조건과 제약사항을 준수하면 요구사항을 다 구현했습니다.
- 하나의 api에 대해 성공 케이스부터 구현한 예외 발생 경우까지 테스트 코드로 다 작성했습니다.
- Restful API 방식으로 설계했습니다.
- 의도를 확실히 드러내어 가독성 있게 작성하도록 노력했습니다.
- 각 api마다 주석을 충분히 설명이 되도록 작성했습니다.

<br>

# 사용 기술

- python 3.11
- django 4.2
- drf 3.14

- 사용된 라이브러리
    - drf-spectacular: API 문서
    - djangorestframework-simplejwt: 인증 및 인가
    - django-environ: 환경 변수 관리

<br>

# 패키지 관리와 Linter, Formatter

- 패키지 관리는 poetry 를 사용했습니다.
- pre-commit-hook 을 통해 black와 flake8 적용했습니다.

<br>

# API 문서

- drf-spectacular 라이브러리를 사용했습니다.
- API 문서 확인하기
    - `docker-compose -f docker-compose-dev.yml` 을 실행합니다.
    - container 생성이 완료되었으면 http://0.0.0.0:8000/api/v1/docs url로 접속합니다.

<br>

# 테스트

- pytest-django를 사용했습니다.
- 테스트 실행 방법: manage.py 가 있는 경로에서 아래 명령어를 입력합니다.
    - 간략하게 테스트 통과 유무를 확인하고 싶으시면 `pytest`를 입력합니다.
    - 자세한 테스트 명과 결과를 보고 싶으시면 `pytest -sv` 를 입력합니다.
- `pytest -svm {marker name}` 을 사용하면 marker name이 있는 테스트 별로 구분해서 실행할 수 있습니다.
    - marker name은 `pytest.ini`에서 확인할 수 있습니다.

<br>

# 데이터베이스 구조

- created_at, modified_at과 통일성을 갖추기 위해 completed_data를 completed_at 수정 부분 외에는 없습니다.
- 테스트를 위한 데이터베이스 환경


# 기타
- Django signal을 사용하여 하위 업무가 모두 완료되면 자동적으로 업무가 완료처리를 구현했습니다. 