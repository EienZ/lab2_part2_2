import boto3
import pandas

def create_key_pair(key_name, region):
    ec2_client = boto3.client("ec2", region_name=region)
    key_pair = ec2_client.create_key_pair(KeyName=key_name)
    private_key = key_pair["KeyMaterial"]
    with open(f"{key_name}.pem", "w+") as handle:
        handle.write(private_key)
    print(f"Ключову пару {key_name} створено та збережено в файлі {key_name}.pem")

def create_instance(image_id, instance_name, instance_type, key_name, region):
    min_count = 1
    max_count = 1
    ec2_client = boto3.client("ec2", region_name=region)
    instances = ec2_client.run_instances(
        ImageId=image_id,
        MinCount=min_count,
        MaxCount=max_count,
        InstanceType=instance_type,
        KeyName=key_name,
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': instance_name
                    },
                ]
            },
        ]
    )
    instance_id = instances["Instances"][0]["InstanceId"]
    print(f"Екземпляр {instance_name} створено з ID: {instance_id}")

def get_running_instances(region):
    ec2_client = boto3.client("ec2", region_name=region)
    reservations = ec2_client.describe_instances().get("Reservations")
    instances_data = []
    for reservation in reservations:
        for instance in reservation["Instances"]:
            instance_id = instance["InstanceId"]
            instance_type = instance["InstanceType"]
            public_ip = instance.get("PublicIpAddress", "N/A")
            private_ip = instance.get("PrivateIpAddress", "N/A")
            instances_data.append((instance_id, instance_type, public_ip, private_ip))
    return instances_data

def stop_instance(instance_id, region):
    ec2_client = boto3.client("ec2", region_name=region)
    response = ec2_client.stop_instances(InstanceIds=[instance_id])
    print(response)

def terminate_instance(instance_id, region):
    ec2_client = boto3.client("ec2", region_name=region)
    response = ec2_client.terminate_instances(InstanceIds=[instance_id])
    print(response)

def create_bucket(bucket_name, region):
    s3_client = boto3.client('s3', region_name=region)
    location = {'LocationConstraint': region}
    response = s3_client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration=location)
    print(response)

def upload(file_name, bucket_name, s3_obj_name):
    s3_client = boto3.client('s3')
    response = s3_client.upload_file(Filename=file_name, Bucket=bucket_name, Key=s3_obj_name)
    print(response)

def destroy_bucket(bucket_name):
    s3_client = boto3.client('s3')
    response = s3_client.delete_bucket(Bucket=bucket_name)
    print(response)

def list_buckets():
    s3 = boto3.client('s3')
    response = s3.list_buckets()
    print('Існуючі бакети:')
    for bucket in response['Buckets']:
        print(f' {bucket["Name"]}')

def read_csv_from_s3(bucket_name, key):
    s3_client = boto3.client('s3')
    obj = s3_client.get_object(
        Bucket=bucket_name,
        Key=key
    )
    data = pandas.read_csv(obj['Body'])
    print('Виведення кадру даних...')
    print(data.head())

region = input("Введіть назву регіону (наприклад, eu-west-2): ")

print("Меню:")
print("1. Створити ключову пару")
print("2. Створити екземпляр")
print("3. Отримати запущені екземпляри")
print("4. Зупинити екземпляр")
print("5. Завершити екземпляр")
print("6. Створити бакет S3")
print("7. Завантажити файл в бакет S3")
print("8. Видалити бакет S3")
print("9. Показати існуючі бакети S3")
print("10. Прочитати CSV з бакету S3")
print("11. Вийти")

while True:
    choice = input("Виберіть опцію: ")

    if choice == "1":
        key_name = input("Введіть назву ключової пари: ")
        create_key_pair(key_name, region)
    elif choice == "2":
        image_id = input("Введіть ID образу: ")
        instance_name = input("Введіть ім'я інстансу: ")
        instance_type = input("Тип екземпляру (наприклад, t4g.nano): ")
        key_name = input("Назва ключової пари: ")
        create_instance(image_id, instance_name, instance_type, key_name, region)
    elif choice == "3":
        instances_data = get_running_instances(region)
        for instance_id, instance_type, public_ip, private_ip in instances_data:
            print(f"ID: {instance_id}, Тип: {instance_type}, Публічна IP: {public_ip}, Приватна IP: {private_ip}")
    elif choice == "4":
        instance_id = input("Введіть ID екземпляру, який потрібно зупинити: ")
        stop_instance(instance_id, region)
    elif choice == "5":
        instance_id = input("Введіть ID екземпляру, який потрібно завершити: ")
        terminate_instance(instance_id, region)
    elif choice == "6":
        bucket_name = input("Введіть назву бакету S3: ")
        create_bucket(bucket_name, region)
    elif choice == "7":
        file_name = input("Введіть шлях до файлу, який потрібно завантажити: ")
        s3_obj_name = input("Введіть ім'я об'єкту S3: ")
        upload(file_name, bucket_name, s3_obj_name)
    elif choice == "8":
        bucket_name = input("Введіть назву бакету S3, який потрібно видалити: ")
        destroy_bucket(bucket_name)
    elif choice == "9":
        list_buckets()
    elif choice == "10":
        bucket_name = input("Введіть назву бакету S3: ")
        key = input("Введіть ключ до CSV-файлу: ")
        read_csv_from_s3(bucket_name, key)
    elif choice == "11":
        break
    else:
        print("Невірний вибір, спробуйте ще раз.")
