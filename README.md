## S3proxy - serve S3 files simply

S3proxy is a simple flask-based REST web application which can expose files (keys) stored in the AWS Simple Storage Service (S3) via a simple REST api. 

### What does this do?
S3proxy takes a set of AWS credentials and an S3 bucket name and provides GET and HEAD endpoints on the files within the bucket. It uses the [boto][boto] library for internal access to S3. For example, if your bucket has the following file:

    s3://mybucket/examples/path/to/myfile.txt

then running S3proxy on a localhost server (port 5000) would enable you read (GET) this file at:

	http://localhost:5000/files/examples/path/to/myfile.txt

Support exists in S3proxy for the `byte-range` header in a GET request. This means that the API can provide arbitrary parts of S3 files if requested/supported by the application making the GET request.

### Why do this?
S3proxy simplifies access to private S3 objects. While S3 already provides [a complete REST API][s3_api], this API requires signed authentication headers or parameters that are not always obtainable within existing applications (see below), or overly complex for simple development/debugging tasks.

In fact, however, S3proxy was specifically designed to provide a compatability layer for viewing DNA sequencing data in(`.bam` files) using [IGV][igv]. While IGV already includes an interface for reading bam files from an HTTP endpoint, it does not support creating signed requests as required by the AWS S3 API (IGV does support HTTP Basic Authentication, a feature that I would like to include in S3proxy in the near future). Though it is in principal possible to provide a signed AWS-compatible URL to IGV, IGV will still not be able to create its own signed URLs necessary for accessing `.bai` index files, usually located in the same directory as the `.bam` file. Using S3proxy you can expose the S3 objects via a simplified HTTP API which IGV can understand and access directly.

### Important considerations and caveats
S3proxy should not be used in production-level or open/exposed servers! There is currently no security provided by S3proxy (though I may add basic HTTP authentication later). Once given the AWS credentials, S3proxy will serve any path available to it. And, although I restrict requests to GET and HEAD only, I cannot currently guarantee that a determined person would not be able to execute a PUT/UPDATE/DELETE request using this service.

Additionally, all the usual recommendations for WSGI applications apply to S3cmd. Don't use the built-in flask debugging server for anything but testing and development! For more information about configuring a WSGI app see [this page][wsgi_server]

Finally, I highly recommend you create a separate [IAM role][iam_roles] in AWS with limited access and permisisons to S3 only for use with S3proxy. 

### Features
   - Serves S3 file objects via standard GET request, optionally providing only a part of a file using the `byte-range` header. 
   - Easy to configure via a the `config.yaml` file-- S3 keys and bucket name is all you need!
   - Uses the werkzeug [`SimpleCache` module][simplecache] to cache S3 object identifiers (but not data) in order to reduce latency and lookup times.

### Future development
   - Implement HTTP Basic Authentication to provide some level of security.
   - Implement other error codes and basic REST responses. 
   - Add ability to log to a file and specify a `--log-level`


[boto]: http://boto.readthedocs.org/
[s3_api]: http://docs.aws.amazon.com/AmazonS3/latest/API/APIRest.html
[igv]: http://www.broadinstitute.org/igv/home
[wsgi_server]: http://flask.pocoo.org/docs/deploying/
[iam_roles]: http://aws.amazon.com/iam/
[simplecache]: http://flask.pocoo.org/docs/patterns/caching/

