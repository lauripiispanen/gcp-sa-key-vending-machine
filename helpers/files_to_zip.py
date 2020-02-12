import base64
import hashlib
from io import BytesIO
import zipfile

class ZipWithFiles:
  def __init__(self, content):
    self.content = content

  def Md5(self):
    m = hashlib.md5()
    m.update(self.content)
    return m.hexdigest()
  
  def ToAscii(self):
    return self.content.decode('ascii')

def Create(ctx, fileName):
  in_memory_output_file = BytesIO()
  zip_file = zipfile.ZipFile(
      in_memory_output_file,
      mode='w',
      compression=zipfile.ZIP_DEFLATED)

  for imp in ctx.imports:
    if imp.startswith(fileName):
      zip_file.writestr(imp[len(fileName):],
                        ctx.imports[imp])
  zip_file.close()
  return ZipWithFiles(base64.b64encode(in_memory_output_file.getvalue()))

