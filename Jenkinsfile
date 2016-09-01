node {
  stage name:"Stage 1: Checkout SCM";
  checkout scm;

  stage name:"Stage 2: Run Ansible Provisioning tests";
  sh 'cd provisioning && kitchen test'

}
