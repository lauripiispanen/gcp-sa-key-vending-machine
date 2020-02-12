from helpers import files_to_zip

def GenerateConfig(ctx):
  helloWorldZipFile = files_to_zip.Create(ctx, 'functions/hello-world.go')
  resources = [{
      'name': 'create-service-account-key',
      'type': 'gcp-types/cloudfunctions-v1:projects.locations.functions',
      'properties': {
          'parent': 'projects/' + (ctx.properties.get("project") or ctx.env["project"]) + '/locations/' + ctx.properties["location"],
          'location': ctx.properties["location"],
          'function': 'create-service-account-key',
          'sourceArchiveUrl': 'gs://$(ref.cloud-function-storage-bucket.name)/' + helloWorldZipFile.Md5() + '.zip',
          'runtime': 'go113',
          'httpsTrigger': {}
      }
    },{
      'name': 'remove-service-account-key',
      'type': 'gcp-types/cloudfunctions-v1:projects.locations.functions',
      'properties': {
          'parent': 'projects/' + (ctx.properties.get("project") or ctx.env["project"]) + '/locations/' + ctx.properties["location"],
          'location': ctx.properties["location"],
          'function': 'remove-service-account-key',
          'sourceArchiveUrl': 'gs://$(ref.cloud-function-storage-bucket.name)/' + helloWorldZipFile.Md5() + '.zip',
          'runtime': 'go113',
          'eventTrigger': {
            'eventType': 'providers/cloud.pubsub/eventTypes/topic.publish',
            'resource': '$(ref.key-deletion-requests-topic.name)'
          }
      }
    },{
      'name': 'key-deletion-requests-topic',
      'type': 'gcp-types/pubsub-v1:projects.topics',
      'properties': {
          'topic': 'key-deletion-requests'
      }
    },{
      'name': 'cloud-function-storage-bucket',
      'type': 'gcp-types/storage-v1:buckets',
      'properties': {
          'name': (ctx.properties.get("project") or ctx.env["project"]) + '-cloud-functions',
          'predefinedAcl': 'projectPrivate',
          'location': ctx.properties["location"],
          'storageClass': 'STANDARD',
          'projection': 'full'
      }
    },{
      'name': 'upload-functions',
      'action': 'gcp-types/cloudbuild-v1:cloudbuild.projects.builds.create',
      'metadata': {
        'runtimePolicy': ['UPDATE_ON_CHANGE']
      },
      'properties': {
        'steps': [{
          'name': 'gcr.io/cloud-builders/gsutil',
          'entrypoint': 'bash',
          'args': [
            '-c',
            'echo \'' + helloWorldZipFile.ToAscii() + '\' | base64 -d | gsutil cp - gs://$(ref.cloud-function-storage-bucket.name)/' + helloWorldZipFile.Md5() + '.zip'
          ]
        }],
        'timeout': '120s'
      }
    },{
      'name': 'cleanup-bucket',
      'action': 'gcp-types/cloudbuild-v1:cloudbuild.projects.builds.create',
      'metadata': {
        'runtimePolicy': ['DELETE']
      },
      'properties': {
        'steps': [{
          'name': 'gcr.io/cloud-builders/gsutil',
          'args': [
            'rm',
            '-r',
            'gs://$(ref.cloud-function-storage-bucket.name)/**'
          ]
        }],
        'timeout': '120s'
      }
    }]

  return {
    'resources': resources,
    'outputs': []    
  }