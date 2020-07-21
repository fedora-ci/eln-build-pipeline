#!groovy

@Library('fedora-pipeline-library@prototype') _

def podYAML = """
spec:
  containers:
  - name: koji
    image: quay.io/bookwar/koji-client:0.0.1
    tty: true
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
	kubernetes {
	    yaml podYAML
	    defaultContainer 'koji'
	}
    }

    parameters {
        string(
	    name: 'KOJI_BUILD_ID',
	    defaultValue: null,
	    trim: true,
	    description: 'Koji build id. Example: 1234547'
	)
    }

    stages {
	stage('Rebuild') {
	    steps {
		withCredentials(
		    [file(credentialsId: 'fedora-keytab', variable: 'KOJI_KEYTAB')]
		) {
		    script {
			currentBuild.description = params.KOJI_BUILD_ID
                	output = sh (returnStdout: True) {
			    './eln-rebuild.py -w -b $KOJI_BUILD_ID'
			}
			currentBuild.description = output.toString().trim()
                    }
		    
		}
            }
	    
	}
    }

    post {
        always {
            echo 'Job completed'
        }
    }
}
