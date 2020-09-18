# Pipeline Linter

A [Pipeline linter](https://www.jenkins.io/doc/book/pipeline/development/#linter) is enabled for this repository.
On each pull-request, it checks Jenkins files syntax.

It can be run locally:

```
MY_JENKINSFILE=some_jenkinsfile
MY_JENKINS_URL=https://my-jenkins-some-project.org

curl -H "Authorization: OAuth " -X POST -F "jenkinsfile=<$MY_JENKINSFILE" $MY_JENKINS_URL/pipeline-model-converter/validate
```
