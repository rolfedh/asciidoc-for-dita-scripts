#!/usr/bin/ruby

require 'asciidoctor'
require 'json'

# This class uses a Treeprocessor to walk the fully parsed document
# tree and map block IDs to their source filenames.

class IdMapper < Asciidoctor::Extensions::Treeprocessor
  def initialize(id_map)
    super()
    @id_map = id_map
    @processed_files = Set.new
  end

  def process(document)
    # Use find_by to recursively traverse every the document tree.
    document.find_by do |block|
      # only blocks that have an ID and a source location.
      if block.id && block.source_location&.path
        id = block.id
        source_file = block.source_location.path

        @id_map[id] = source_file
        
        # Log to the console to show progress.
        unless @processed_files.include?(source_file)
          puts "📖 Processing file: #{source_file}"
          @processed_files.add(source_file)
        end
        puts "  -> Found ID: '#{id}'"
      end
      # Return true to continue traversal (the default for find_by).
    end
    document # A Treeprocessor should return the document.
  end
end


unless ARGV.length == 2
  puts "Usage: ruby map_ids_final.rb <master.adoc> <output.json>"
  exit 1
end

master_file = ARGV[0]
output_file = ARGV[1]

# This external hash will be populated by our extension.
id_dictionary = {}

puts "Starting recursive scan from '#{master_file}'..."

# Register the custom treeprocessor with Asciidoctor.
Asciidoctor::Extensions.register do
  treeprocessor(IdMapper.new(id_dictionary))
end

begin
  # Use Asciidoctor.convert to ensure the full pipeline runs,
  # including the Treeprocessor stage. We'll discard the output.
  Asciidoctor.convert_file(
    master_file,
    safe: :unsafe,          # Allow reading included files.
    catalog_assets: true,   # Ensure includes are resolved.
    to_file: false,         # Don't create an HTML output file.
    sourcemap: true         # Enable source_location tracking.
  )

  # Write dictionary to JSON file.
  File.open(output_file, 'w') do |file|
    file.write(JSON.pretty_generate(id_dictionary.sort.to_h))
  end
  
  puts "\n--------------------------------------------------"
  puts "✅ Success! Created '#{output_file}' with #{id_dictionary.length} entries."

rescue StandardError => e
  puts "\nAn error occurred: #{e}"
  puts e.backtrace
  exit 1
end
