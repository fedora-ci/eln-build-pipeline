#!groovy

@Library('fedora-pipeline-library@prototype') _

def podYAML = """
spec:
  containers:
  - name: koji
    image: quay.io/bookwar/koji-client:0.0.1
"""

def pipelineMetadata = [
    pipelineName: 'eln-build',
    pipelineDescription: 'Rebuild Fedora Rawhide package in the ELN Buildroot',
    testCategory: 'eln',
    testType: 'build',
    maintainer: 'Fedora CI',
    docs: 'https://github.com/fedora-ci/eln-build-pipeline',
    contact: [
        irc: '#fedora-ci',
        email: 'ci@lists.fedoraproject.org'
    ],
]

def artifactId

pipeline {

    options {
        buildDiscarder(logRotator(daysToKeepStr: '180', artifactNumToKeepStr: '100'))
	timeout(time: 4, unit: 'HOURS') 
    }

    agent {
        label 'fedora-ci-'.concat(pipelineMetadata.pipelineName)
	kubernetes {
	    yaml podYAML
	}
    }

    parameters {
        string(
	    name: 'ARTIFACT_ID',
	    defaultValue: null,
	    trim: true,
	    description: '"koji-build:<taskId>" for Koji builds; Example: koji-build:42376994'
	)
	string(
	    name: 'ADDITIONAL_ARTIFACT_IDS',
	    defaultValue: null,
	    trim: true,
	    description: 'A comma-separated list of additional ARTIFACT_IDs'
	)
    }

    stages {
        stage('Prepare') {
            steps {
                script {
                    artifactId = params.ARTIFACT_ID

                    if (!artifactId) {
                        abort('ARTIFACT_ID is missing')
                    }
                }
                setBuildNameFromArtifactId(artifactId: artifactId)
            }
        }

        stage('Test') {
            steps {
		sh 'koji list-targets --name=eln'
            }
        }
    }

    post {
        always {
            echo 'Job completed'
        }
    }
}
