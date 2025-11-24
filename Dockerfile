
# FROM public.ecr.aws/lambda/python:3.9

# # Install system dependencies required by OpenCV / RealESRGAN New code
# RUN yum install -y mesa-libGL mesa-libGLU

# # Copy function code
# COPY lambda_function/* ${LAMBDA_TASK_ROOT}/

# # Install dependencies
# COPY requirements.txt .
# RUN pip install -r requirements.txt

# # Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
# CMD [ "lambda_function.lambda_handler" ]


# FROM public.ecr.aws/lambda/python:3.9

# # Install system dependencies for RealESRGAN / OpenCV / Pillow
# RUN yum install -y \
#     mesa-libGL \
#     mesa-libGLU \
#     libgcc \
#     libstdc++ \
#     && yum clean all

# # Copy function code
# COPY lambda_function/* ${LAMBDA_TASK_ROOT}/

# # Install Python dependencies
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# # Lambda handler
# CMD ["lambda_function.lambda_handler"]

FROM public.ecr.aws/lambda/python:3.9

# Install system dependencies
RUN yum install -y \
    mesa-libGL \
    mesa-libGLU \
    libgcc \
    libstdc++ \
    && yum clean all

# Set PYTHONPATH so Lambda can import the handler
ENV PYTHONPATH="${LAMBDA_TASK_ROOT}"

# Copy function code
COPY lambda_function/ ${LAMBDA_TASK_ROOT}/

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt -t ${LAMBDA_TASK_ROOT}

CMD ["lambda_function.lambda_handler"]

