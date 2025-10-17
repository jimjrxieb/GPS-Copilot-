# 1. Download AWS CLI installer
cd ~
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"

# 2. Install unzip if needed
sudo apt install unzip -y

# 3. Unzip installer
unzip awscliv2.zip

# 4. Run installer
sudo ./aws/install

# 5. Verify installation
aws --version

# Should show: aws-cli/2.x.x Python/3.x.x Linux/x.x.x
