# Terraform + OPA Integration Complete Tutorial

## Overview
Terraform lets you describe the infrastructure you want and automatically creates, deletes, and modifies your existing infrastructure to match. OPA makes it possible to write policies that test the changes Terraform is about to make before it makes them. Such tests help in different ways:

- Tests help individual developers sanity check their Terraform changes
- Tests can auto-approve run-of-the-mill infrastructure changes and reduce the burden of peer-review
- Tests can help catch problems that arise when applying Terraform to production after applying it to staging

Terraform is a popular integration case for OPA and there are already a number of popular tools for running policy on HCL and plan JSONs.

## Goals
In this tutorial, you'll learn how to use OPA to implement unit tests for Terraform plans that create and delete auto-scaling groups and servers.

## Prerequisites
This tutorial requires:
- Terraform 0.12.6+
- OPA

## Getting Started

### Step 1: Create and Save a Terraform Plan

Create a Terraform file that includes an auto-scaling group and a server on AWS:

```hcl
provider "aws" {
    region = "us-west-1"
}

resource "aws_instance" "web" {
  instance_type = "t2.micro"
  ami = "ami-09b4b74c"
}

resource "aws_autoscaling_group" "my_asg" {
  availability_zones        = ["us-west-1a"]
  name                      = "my_asg"
  max_size                  = 5
  min_size                  = 1
  health_check_grace_period = 300
  health_check_type         = "ELB"
  desired_capacity          = 4
  force_delete              = true
  launch_configuration      = "my_web_config"
}

resource "aws_launch_configuration" "my_web_config" {
    name = "my_web_config"
    image_id = "ami-09b4b74c"
    instance_type = "t2.micro"
}
```

Then initialize Terraform and create a plan:

```bash
terraform init
terraform plan --out tfplan.binary
```

### Step 2: Convert the Terraform Plan into JSON

Use the command terraform show to convert the Terraform plan into JSON so that OPA can read the plan:

```bash
terraform show -json tfplan.binary > tfplan.json
```

### Step 3: Understanding Terraform JSON Plan Structure

The JSON plan output contains critical information for policy evaluation:

- **`.resource_changes`**: Array containing all actions that terraform will apply
- **`.resource_changes[].type`**: The type of resource (e.g. aws_instance, aws_iam)
- **`.resource_changes[].change.actions`**: Array of actions applied on the resource (create, update, delete)

### Step 4: Write the OPA Policy to Check the Plan

The policy computes a score for a Terraform plan that combines:
- The number of deletions of each resource type
- The number of creations of each resource type
- The number of modifications of each resource type

**policy/terraform.rego:**

```rego
package terraform.analysis

import input as tfplan

########################
# Parameters for Policy
########################

# acceptable score for automated authorization
blast_radius := 30

# weights assigned for each operation on each resource-type
weights := {
    "aws_autoscaling_group": {"delete": 100, "create": 10, "modify": 1},
    "aws_instance": {"delete": 10, "create": 1, "modify": 1},
}

# Consider exactly these resource types in calculations
resource_types := {"aws_autoscaling_group", "aws_instance", "aws_iam", "aws_launch_configuration"}

#########
# Policy
#########

# Authorization holds if score for the plan is acceptable and no changes are made to IAM
default authz := false

authz if {
    score < blast_radius
    not touches_iam
}

# Compute the score for a Terraform plan as the weighted sum of deletions, creations, modifications
score := s if {
    all_resources := [x |
        some resource_type, crud in weights

        del := crud.delete * num_deletes[resource_type]
        new := crud.create * num_creates[resource_type]
        mod := crud.modify * num_modifies[resource_type]
        x := (del + new) + mod
    ]
    s := sum(all_resources)
}

# Whether there is any change to IAM
touches_iam if {
    all_resources := resources.aws_iam
    count(all_resources) > 0
}

####################
# Terraform Library
####################

# list of all resources of a given type
resources[resource_type] := all_resources if {
    some resource_type, _ in resource_types

    all_resources := [name |
        some name in tfplan.resource_changes
        name.type == resource_type
    ]
}

# number of creations of resources of a given type
num_creates[resource_type] := num if {
    some resource_type, _ in resource_types

    all_resources := resources[resource_type]
    creates := [res |
        some res in all_resources
        "create" in res.change.actions
    ]
    num := count(creates)
}

# number of deletions of resources of a given type
num_deletes[resource_type] := num if {
    some resource_type, _ in resource_types

    all_resources := resources[resource_type]

    deletions := [res |
        some res in all_resources
        "delete" in res.change.actions
    ]
    num := count(deletions)
}

# number of modifications to resources of a given type
num_modifies[resource_type] := num if {
    some resource_type, _ in resource_types

    all_resources := resources[resource_type]

    modifies := [res |
        some res in all_resources
        "update" in res.change.actions
    ]
    num := count(modifies)
}
```

### Step 5: Evaluate the OPA Policy on the Terraform Plan

To evaluate the policy against the plan:

```bash
opa exec --decision terraform/analysis/authz --bundle policy/ tfplan.json
```

Expected output:
```json
{
  "result": [
    {
      "path": "tfplan.json",
      "result": true
    }
  ]
}
```

Check the score that the policy used to make the authorization decision:

```bash
opa exec --decision terraform/analysis/score --bundle policy/ tfplan.json
```

Expected output (score of 11):
```json
{
  "result": [
    {
      "path": "tfplan.json",
      "result": 11
    }
  ]
}
```

### Step 6: Create a Large Terraform Plan and Test Policy Enforcement

Create a Terraform plan that creates enough resources to exceed the blast-radius:

```hcl
provider "aws" {
    region = "us-west-1"
}

resource "aws_instance" "web" {
  instance_type = "t2.micro"
  ami = "ami-09b4b74c"
}

resource "aws_autoscaling_group" "my_asg" {
  availability_zones        = ["us-west-1a"]
  name                      = "my_asg"
  max_size                  = 5
  min_size                  = 1
  health_check_grace_period = 300
  health_check_type         = "ELB"
  desired_capacity          = 4
  force_delete              = true
  launch_configuration      = "my_web_config"
}

resource "aws_launch_configuration" "my_web_config" {
    name = "my_web_config"
    image_id = "ami-09b4b74c"
    instance_type = "t2.micro"
}

resource "aws_autoscaling_group" "my_asg2" {
  availability_zones        = ["us-west-2a"]
  name                      = "my_asg2"
  max_size                  = 6
  min_size                  = 1
  health_check_grace_period = 300
  health_check_type         = "ELB"
  desired_capacity          = 4
  force_delete              = true
  launch_configuration      = "my_web_config"
}

resource "aws_autoscaling_group" "my_asg3" {
  availability_zones        = ["us-west-2b"]
  name                      = "my_asg3"
  max_size                  = 7
  min_size                  = 1
  health_check_grace_period = 300
  health_check_type         = "ELB"
  desired_capacity          = 4
  force_delete              = true
  launch_configuration      = "my_web_config"
}
```

Generate and evaluate the plan:

```bash
terraform init
terraform plan --out tfplan_large.binary
terraform show -json tfplan_large.binary > tfplan_large.json

opa exec --decision terraform/analysis/authz --bundle policy/ tfplan_large.json
opa exec --decision terraform/analysis/score --bundle policy/ tfplan_large.json
```

This should fail authorization due to exceeding the blast radius threshold.

### Step 7: Remote Policy Bundle Distribution

Build policies into a bundle:

```bash
opa build policy/
```

Serve the bundle via nginx:

```bash
docker run --rm --name bundle_server -d -p 8888:80 -v ${PWD}:/usr/share/nginx/html:ro nginx:latest
```

Run opa exec with bundles enabled:

```bash
opa exec --decision terraform/analysis/authz \
  --set services.bundle_server.url=http://localhost:8888 \
  --set bundles.tutorial.resource=bundle.tar.gz \
  tfplan_large.json
```

## Working with Terraform Modules

### Module Integration Steps

#### Step 1: Create Terraform Module Plan

Create a Terraform file using modules:

```hcl
provider "aws" {
  region = "us-east-1"
}

data "aws_vpc" "default" {
  default = true
}

module "http_sg" {
  source = "git::https://github.com/terraform-aws-modules/terraform-aws-security-group.git?ref=v3.10.0"

  name        = "http-sg"
  description = "Security group with HTTP ports open for everybody (IPv4 CIDR), egress ports are all world open"
  vpc_id      = data.aws_vpc.default.id

  ingress_cidr_blocks = ["0.0.0.0/0"]
}

resource "aws_security_group" "allow_tls" {
  name        = "allow_tls"
  description = "Allow TLS inbound traffic"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "TLS from VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/8"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "allow_tls"
  }
}
```

Generate the plan:

```bash
terraform init
terraform plan --out tfplan.binary
terraform show -json tfplan.binary > tfplan2.json
```

#### Step 2: Write OPA Policy for Module Resources

**policy/terraform_module.rego:**

```rego
package terraform.module

deny contains msg if {
    some r
    desc := resources[r].values.description
    contains(desc, "HTTP")
    msg := sprintf("No security groups should be using HTTP. Resource in violation: %v", [r.address])
}

resources contains r if {
    some path, value

    # Walk over the JSON tree and check if the node we are
    # currently on is a module (either root or child) resources
    walk(input.planned_values, [path, value])

    # Look for resources in the current value based on path
    some r in module_resources(path, value)
}

# Variant to match root_module resources
module_resources(path, value) := value if {
    # Expect something like:
    #     {
    #         "root_module": {
    #             "resources": [...],
    #             ...
    #         }
    #         ...
    #     }
    # Where the path is [..., "root_module", "resources"]

    reverse_index(path, 1) == "resources"
    reverse_index(path, 2) == "root_module"
}

# Variant to match child_modules resources
module_resources(path, value) := value if {
    # Expect something like:
    #     {
    #         ...
    #         "child_modules": [
    #             {
    #                 "resources": [...],
    #                 ...
    #             },
    #             ...
    #         ]
    #         ...
    #     }
    # Where the path is [..., "child_modules", 0, "resources"]

    reverse_index(path, 1) == "resources"
    reverse_index(path, 3) == "child_modules"
}

reverse_index(path, idx) := path[count(path) - idx]
```

#### Step 3: Evaluate Module Policy

```bash
opa exec --decision terraform/module/deny --bundle policy/ tfplan2.json
```

Expected output identifying the HTTP security group violation:

```json
{
  "result": [
    {
      "path": "tfplan2.json",
      "result": [
        "No security groups should be using HTTP. Resource in violation: module.http_sg.aws_security_group.this_name_prefix[0]"
      ]
    }
  ]
}
```

## Advanced Integration Patterns

### CI/CD Pipeline Integration

#### GitHub Actions Example

```yaml
name: Terraform OPA Validation
on: [push, pull_request]

jobs:
  terraform-policy-check:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2

    - name: Setup Terraform
      uses: hashicorp/setup-terraform@v1
      with:
        terraform_version: 0.14.7

    - name: Setup OPA
      run: |
        curl -L -o opa https://github.com/open-policy-agent/opa/releases/latest/download/opa_linux_amd64
        chmod +x opa
        sudo mv opa /usr/local/bin/

    - name: Terraform Plan
      run: |
        terraform init
        terraform plan -out=tfplan.binary
        terraform show -json tfplan.binary > tfplan.json

    - name: OPA Policy Check
      run: |
        opa exec --decision terraform/analysis/authz --bundle policy/ tfplan.json
        opa exec --decision terraform/analysis/score --bundle policy/ tfplan.json
```

### Enterprise Policy Management

#### Centralized Policy Repository Structure

```
policy-repo/
├── terraform/
│   ├── aws/
│   │   ├── security_groups.rego
│   │   ├── iam.rego
│   │   └── compute.rego
│   ├── azure/
│   │   ├── network.rego
│   │   └── storage.rego
│   └── gcp/
│       ├── compute.rego
│       └── storage.rego
├── kubernetes/
│   ├── security.rego
│   └── resources.rego
└── tests/
    ├── terraform_test.rego
    └── kubernetes_test.rego
```

#### Policy Testing Framework

```rego
package terraform.analysis.test

test_small_plan_authorized if {
    authz with input as {
        "resource_changes": [
            {
                "type": "aws_instance",
                "change": {"actions": ["create"]}
            }
        ]
    }
}

test_large_plan_denied if {
    not authz with input as {
        "resource_changes": [
            {
                "type": "aws_autoscaling_group",
                "change": {"actions": ["create"]}
            },
            {
                "type": "aws_autoscaling_group",
                "change": {"actions": ["create"]}
            },
            {
                "type": "aws_autoscaling_group",
                "change": {"actions": ["create"]}
            },
            {
                "type": "aws_autoscaling_group",
                "change": {"actions": ["create"]}
            }
        ]
    }
}
```

## Integration with GP-Copilot Security Framework

### Automated Policy Enforcement Workflow

When GP-Copilot encounters Terraform plans, Jade should:

1. **Plan Analysis**: Extract and analyze Terraform JSON plans
2. **Policy Evaluation**: Run OPA policies against infrastructure changes
3. **Risk Assessment**: Calculate blast radius and security impact
4. **Compliance Mapping**: Map violations to security frameworks
5. **Remediation Guidance**: Provide specific fixes for policy violations

### Security Policy Categories

#### Infrastructure Security Policies
- Resource tagging requirements
- Network security configurations
- IAM permission boundaries
- Encryption enforcement

#### Operational Security Policies
- Change impact assessment
- Blast radius limitations
- Approval workflow triggers
- Rollback procedures

#### Compliance Policies
- Regulatory requirement validation
- Audit trail generation
- Documentation standards
- Security control verification

### Escalation Criteria for Terraform + OPA

- **Critical**: IAM changes, public resource exposure, encryption violations
- **High**: Large blast radius, missing security controls, compliance violations
- **Medium**: Tagging violations, suboptimal configurations, policy warnings
- **Low**: Documentation gaps, optimization opportunities

This comprehensive tutorial provides hands-on experience with Terraform policy enforcement using OPA, enabling automated security validation and compliance checking in infrastructure deployment pipelines.