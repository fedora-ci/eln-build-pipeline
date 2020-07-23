#!groovy

@Library('fedora-pipeline-library@prototype') _

import org.fedoraproject.jenkins.koji.Koji

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

def buildDescriptionFile
def kojiBuildId

pipeline {

    options {
	buildDiscarder(logRotator(daysToKeepStr: '180', artifactNumToKeepStr: '100'))
	timeout(time: 4, unit: 'HOURS')
	throttle(['eln-build'])
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
	stage('Preparing input') {
	    steps {
		script {
		    kojiBuildId = params.KOJI_BUILD_ID.toInteger()
		    def koji = new Koji()
		    build = koji.getBuildInfo(kojiBuildId)
		    currentBuild.description = build.nvr

		    buildDescriptionFile = 'output.txt'
		}
	    }
	}
	stage('Rebuild') {
	    environment {
		KOJI_KEYTAB = credentials('fedora-keytab')
	    }

	    steps {
		sh "./eln-rebuild.py -w -b $kojiBuildId -o $buildDescriptionFile"
	    }
	}
    }

    post {
	always {
	    script {
		try {
		    currentBuild.description = readFile(buildDescriptionFile)
		} catch (Exception e) {
		    echo e.toString()
		}
	    }
	}
    }
}
