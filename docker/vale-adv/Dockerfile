FROM jdkato/vale:latest

# Pre-install the ADV ruleset
RUN vale sync --config=/dev/null jhradilek/asciidoctor-dita-vale

# Set working directory
WORKDIR /docs

# Use Vale directly as entrypoint
ENTRYPOINT ["vale"]