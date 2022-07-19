import os
import sys

# insert at position 1 in the path, as 0 is the path of this file.
sys.path.insert(1, '/Users/dpalaia/projects/test2/common_code')

from create_overlay import create_overlay

if len(sys.argv) == 2:
   print('the script needs at least a cluster operator manifests and version as arguments in order to create the OLM structure')
   sys.exit()

operator_release_file = sys.argv[1] 
version = sys.argv[2]

# Apply version to the service-version generator
ytt_command_add_version = "ytt -f ./generators/cluster-service-version-generator.yml --data-value-yaml name=rabbitmq-cluster-operator.v"+version+" --data-value-yaml version="+version+ "> ./tmpmanifests/cluster-service-version-generator.yaml"
os.system(ytt_command_add_version)
# Create a copy of the cluster operator and add --- at the end of the file
cluster_operator_release_file = "./generators/cluster-operator.yaml"

os.system("cp " + operator_release_file + " " + cluster_operator_release_file)
os.system("echo \"\n---\" >> "+cluster_operator_release_file )

# Finalize the overlay
create_overlay(cluster_operator_release_file, "kind: Role", "rules:", "---", "./generators/overlay-permission-generator.yaml", "./overlays/overlay-permission.yaml")       
create_overlay(cluster_operator_release_file, "kind: ClusterRole", "rules:", "---", "./generators/overlay-cluster-permission-generator.yaml", "./overlays/overlay-cluster-permission.yaml")    
create_overlay(cluster_operator_release_file, "kind: Deployment", "spec:", "terminationGracePeriodSeconds", "./generators/overlay-deployment-generator.yaml", "./overlays/overlay-deployment.yaml")  

# Apply the overlay and generate the ClusterServiceVersion file from overlay
os.system("ytt -f ./overlays/overlay-permission.yaml -f ./tmpmanifests/cluster-service-version-generator.yaml  > ./tmpmanifests/cluster-service-version-permission.yaml")
os.system("ytt -f ./overlays/overlay-cluster-permission.yaml -f ./tmpmanifests/cluster-service-version-permission.yaml > ./tmpmanifests/cluster-service-version-cluster-permission.yaml")
os.system("ytt -f ./overlays/overlay-deployment.yaml -f ./tmpmanifests/cluster-service-version-cluster-permission.yaml > ./generators/cluster-service-version.yaml")

# Create the bundle structure
rabbitmq_cluster_operator_dir="./../../OLM/rabbitmq-cluster-operator/" + version 
rabbitmq_cluster_operator_dir_manifests=rabbitmq_cluster_operator_dir+"/manifests"
os.system("mkdir -p ./../../OLM/rabbitmq-cluster-operator/" + version + "/manifests")
os.system("cp ./generators/cluster-service-version.yaml " + rabbitmq_cluster_operator_dir_manifests)
os.system("cp ./generators/cluster-service-version.yaml " + rabbitmq_cluster_operator_dir_manifests)
os.system("cp ./generators/bundle.Dockerfile " + rabbitmq_cluster_operator_dir)
os.system("cp ./manifests_crds/crds.yaml " + rabbitmq_cluster_operator_dir_manifests)
os.system("cp -fR ./metadata/metadata " + rabbitmq_cluster_operator_dir)






