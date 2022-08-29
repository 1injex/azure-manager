# Docker Version
https://hub.docker.com/r/1injex/azure-manager

# How to use Azure-Manager
1. Launch Docker image:
```bash
docker run -itd --name azure-manager -p 8888:8888 1injex/azure-manager
```
2. Set up your Azure-Manager Admin User:
```bash
# replace username with yours
# replace password with yours
docker exec -it azure-manager flask admin username password
```
3. Visit http://yourip:8888 Let's Azure now!!!
- Your VM Default SSH Credential:
    - USERNAME : defaultuser
    - PASSWORD : Thisis.yourpassword1

# How to get ApiKey String:
1. Input command below into Azure cloud shell(using Bash)
```bash
sub_id=$(az account list --query [].id -o tsv) && az ad sp create-for-rbac --role contributor --scopes /subscriptions/$sub_id
```
2. Format your ApiKey string
## Example 
There will be some output like this:
```json
# Creating 'contributor' role assignment under scope '/subscriptions/DDD'
# The output includes credentials that you must protect. Be sure that you do not include these credentials in your code or check the credentials into your source control. For more information, # see https://aka.ms/azadsp-cli
{
  "appId": "AAA",
  "displayName": "azure-cli",
  "password": "BB",
  "tenant": "CCC"
}
```
ApiKey string Format: 
```
appId|password|tenant|subscriptions
```
So the final ApiKey is: 
```
AAA|BBB|CCC|DDD
```
