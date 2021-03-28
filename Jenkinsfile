pipeline {
    agent {
        dockerfile {
            args '-u root --net=host -v $HOME/docker_volumes/.cache/:/root/.cache/'
        }
    }
    environment {
        SPHINXOPTS = '-w sphinx-build.log'
        DEPLOY_HOST = 'docs@moriya.zapto.org'
        WEBSITE = 'https://moriya.zapto.org'
        PROJECT_NAME = 'discorn'
        DOC_PATH = "/docs/${env.PROJECT_NAME}/"
        REL_PATH = "/releases/${env.PROJECT_NAME}/"
        DEPLOY_DOC_PATH = "www${env.DOC_PATH}"
        DEPLOY_REL_PATH = "www${env.REL_PATH}"
        RELEASE_ROOT = "."
        TAG_NAME = """${TAG_NAME ?: ""}"""
        ARTIFACTS = "${WORKSPACE}/.artifacts"
        WEBHOOK_URL = credentials('webhook_discorn')
    }
    stages {
        stage('Install Dependencies') {
            steps {
                sh 'git clean -fxd'
                sh 'pipenv sync --verbose --sequential --dev'
            }
        }
        stage('Build sources') {
            steps {
                sh 'make -j4'
            }
        }
        stage('Build Python Documentation') {
            steps {
                sh 'make sphinx'
                sh 'mkdir -p ${ARTIFACTS}/doc'
                sh 'tar -C doc/sphinx_src/build/html -czf ${ARTIFACTS}/doc/html.tar.gz .'
            }
            post {
                success {
                    archiveArtifacts artifacts: ".artifacts/doc/*tar.gz", fingerprint: true
                }
                failure {
                    sh 'cat doc/sphinx_src/sphinx-build.log'
                }
            }
        }
        stage('Build Protocol Documentation') {
            steps {
                sh 'make latex'
                sh 'mkdir -p ${ARTIFACTS}/doc/latex'
                sh 'cp doc/LaTeX_src/*.pdf ${ARTIFACTS}/doc/latex/ '
            }
            post {
                success {
                    archiveArtifacts artifacts: ".artifacts/doc/latex/*.pdf", fingerprint: true
                }
                failure {
                    sh 'cat doc/LaTeX_src/*.log'
                }
            }
        }
        stage('Generate release archives') {
            steps {
                sh 'mkdir -p ${ARTIFACTS}/build'
                sh 'mkdir -p /tmp/build'
                sh 'pipenv lock -r | tee ${RELEASE_ROOT}/requirements.txt'
                sh 'echo .artifacts >> .releaseignore'
                sh 'rsync -avr --exclude-from=.releaseignore ${RELEASE_ROOT}/ /tmp/build'
                sh 'tar -C /tmp/build -cvzf ${ARTIFACTS}/build/${TAG_NAME:-${GIT_BRANCH#*/}}.tar.gz --owner=0 --group=0 .'
                sh 'cd /tmp/build && zip ${ARTIFACTS}/build/${TAG_NAME:-${GIT_BRANCH#*/}}.zip -r .'
            }
            post {
                always {
                    archiveArtifacts artifacts: ".artifacts/build/*", fingerprint: true
                }
            }
        }

        stage('Run Tests') { 
            steps {
                sh '''pipenv run python -m pytest -p no:warnings --junit-xml test-reports/results.xml'''
            }
            post {
                always {
                    junit 'test-reports/results.xml' 
                }
            }
        }

        stage('Deploy Documentation') {
            when {
                anyOf {
                    branch 'stable'
                    branch 'master'
                    buildingTag()
                }
            }
            steps {
                sshagent(credentials: ['docs_pk']) {
                    sh 'echo ${TAG_NAME:-${GIT_BRANCH#*/}}'
                    sh 'echo ${DEPLOY_HOST}:${DEPLOY_DOC_PATH}${TAG_NAME:-${GIT_BRANCH#*/}}/'
                    sh 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes ${DEPLOY_HOST} mkdir -p ${DEPLOY_DOC_PATH}${TAG_NAME:-${GIT_BRANCH#*/}}/'
                    sh '''rsync -aze 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes' \
                    --log-file=rsync-doc.log \
                    --delete \
                    doc/sphinx_src/build/html/ ${DEPLOY_HOST}:${DEPLOY_DOC_PATH}${TAG_NAME:-${GIT_BRANCH#*/}}/'''
                    sh 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes ${DEPLOY_HOST} mkdir -p ${DEPLOY_DOC_PATH}/latex/${TAG_NAME:-${GIT_BRANCH#*/}}/'
                    sh '''rsync -aze 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes' \
                    --log-file=rsync-doc.log \
                    --delete \
                    ${ARTIFACTS}/doc/latex/ ${DEPLOY_HOST}:${DEPLOY_DOC_PATH}/latex/${TAG_NAME:-${GIT_BRANCH#*/}}/'''
                }
            }
            post {
                failure {
                    sh 'cat rsync-doc.log'
                }
            }
        }
        
        stage('Deploy Release Files') {
            when {
                anyOf {
                    branch 'stable'
                    branch 'master'
                    buildingTag()
                }
            }
            steps {
                sshagent(credentials: ['docs_pk']) {
                    sh 'echo ${TAG_NAME:-${GIT_BRANCH#*/}}'
                    sh 'echo ${DEPLOY_HOST}:${DEPLOY_REL_PATH}${TAG_NAME:-${GIT_BRANCH#*/}}/'
                    sh 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes ${DEPLOY_HOST} mkdir -p ${DEPLOY_REL_PATH}${TAG_NAME:-${GIT_BRANCH#*/}}/'
                    sh '''rsync -aze 'ssh -o StrictHostKeyChecking=no -o BatchMode=yes' \
                    --log-file=rsync-rel.log \
                    --delete \
                    ${ARTIFACTS}/ ${DEPLOY_HOST}:${DEPLOY_REL_PATH}${TAG_NAME:-${GIT_BRANCH#*/}}/'''
                }
            }
            post {
                failure {
                    sh 'cat rsync-rel.log'
                }
            }
        }
    }
    post {
        always {
            sh 'git clean -fxd'
            discordSend description: env.TAG_NAME ? "Le tag ${env.TAG_NAME} a fini d'exécuter :\n - [Documentation](${env.WEBSITE + env.DOC_PATH + env.TAG_NAME + '/'}) \n - [Release](${env.WEBSITE + env.REL_PATH + env.TAG_NAME + '/'})" : env.BRANCH_NAME == 'stable' || env.BRANCH_NAME == 'master' || env.BRANCH_NAME == 'jenkins_tests' ? "La branche ${env.BRANCH_NAME} a fini d'exécuter :\n - [Documentation](${env.WEBSITE + env.DOC_PATH + env.BRANCH_NAME + '/'}) \n - [Release](${env.WEBSITE + env.REL_PATH + env.BRANCH_NAME + '/'})\n *Note : Ces liens mènent vers la dernière Documentation / Release produite.*" : '*pour plus de détail, voir lien au dessus.*', footer: currentBuild.durationString.replace(" and counting",""), link: env.RUN_DISPLAY_URL, result: currentBuild.currentResult, title:"[${currentBuild.currentResult}] ${currentBuild.fullDisplayName}", webhookURL: env.WEBHOOK_URL
        }
    }
}
