import os
import sys

if len(sys.argv) == 2:
   print('the script needs at least a cluster operator manifests and version as arguments in order to create the OLM structure')
   sys.exit()

operator_release_file = sys.argv[1] 
version = sys.argv[2]

# This function complete an overlay generator file (in ./generators) for Role, Clusterrole and Deployment
def create_overlay(release_file, kind, firstString, endString, file_generator, file_output):

    found = False
    parsing = False


    with open(release_file, 'r') as myfile:

        filestring = ""

        for line in myfile:
            if parsing == True:
    
                if line.find(endString) >=0:
                    if found == True:
                        os.system("cp " + str(file_generator) + " " + str(file_output))
                        with open(file_output, 'a') as myfile:
                            myfile.write(filestring)
                            found = False
                            parsing = False
                            filestring = ""
                            break
              
                if kind !=  "kind: ValidatingWebhookConfiguration":
                    filestring = filestring + "            " + line
                else:
                    filestring = filestring + "    " + line
            if found == True:
                if (line.find(firstString) >= 0): 
                    parsing = True
  

            if line.find(kind) >= 0:
                found = True

# Create a copy of the cluster operator file and add --- at the end of the file
cluster_operator_release_file = "./generators/messaging-topology-operator.yaml"

os.system("cp " + operator_release_file + " " + cluster_operator_release_file)
os.system("echo \"---\" >> "+cluster_operator_release_file )

# Finalize the overlay
create_overlay(cluster_operator_release_file, "kind: Role", "rules:", "---", "./generators/overlay-permission-generator.yaml", "./overlays/overlay-permission.yaml")       
create_overlay(cluster_operator_release_file, "kind: ClusterRole", "rules:", "---", "./generators/overlay-cluster-permission-generator.yaml", "./overlays/overlay-cluster-permission.yaml")    
create_overlay(cluster_operator_release_file, "kind: Deployment", "spec:", "---", "./generators/overlay-deployment-generator.yaml", "./overlays/overlay-deployment.yaml")  
create_overlay(cluster_operator_release_file, "kind: ValidatingWebhookConfiguration", "admissionReviewVersions", "---", "./generators/overlay-webhook-generator.yaml", "./overlays/overlay-weebhook.yaml")  

# Apply the overlay and generate the ClusterServiceVersion file
os.system("ytt -f ./overlays/overlay-permission.yaml -f ./generators/cluster-service-version-generator.yml  > ./tmpmanifests/cluster-service-version-permission.yaml")
os.system("ytt -f ./overlays/overlay-cluster-permission.yaml -f ./tmpmanifests/cluster-service-version-permission.yaml > ./tmpmanifests/cluster-service-version-cluster-permission.yaml")
os.system("ytt -f ./overlays/overlay-deployment.yaml -f ./tmpmanifests/cluster-service-version-cluster-permission.yaml > ./tmpmanifests/cluster-service-version-cluster-deployment.yaml")
os.system("ytt -f ./overlays/overlay-weebhook.yaml -f ./tmpmanifests/cluster-service-version-cluster-deployment.yaml > ./generators/cluster-service-version.yaml")

# Create the structure
rabbitmq_cluster_operator_dir="./../../OLM/rabbitmq-messaging-topology-operator/" + version 
os.system("mkdir -p ./../../OLM/rabbitmq-messaging-topology-operator/" + version + "/manifests")
os.system("cp ./generators/cluster-service-version.yaml " + rabbitmq_cluster_operator_dir+"/manifests")
os.system("cp ./manifests_crds/*.yaml " + rabbitmq_cluster_operator_dir+"/manifests")
os.system("cp -fR ./metadata/ " + rabbitmq_cluster_operator_dir+"/metadata")






