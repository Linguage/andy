#!/usr/bin/env ruby
# frozen_string_literal: true

require "csv"

file = File.expand_path("../contents/data/publications.csv", __dir__)
rows = CSV.read(file, headers: true)

required_columns = %w[id title year type authors venue links tags lang]
required_values = %w[id title year type venue lang]
allowed_types = %w[thesis manuscript journal conference chapter report_trita report_kth]
allowed_langs = %w[en mixed]
errors = []

missing_columns = required_columns - rows.headers
unless missing_columns.empty?
  abort "ERROR: publications.csv missing required columns: #{missing_columns.join(', ')}"
end

ids = {}

rows.each_with_index do |row, idx|
  label = "row #{idx + 2}"

  required_values.each do |key|
    value = row[key].to_s.strip
    errors << "#{label}: missing required field '#{key}'" if value.empty?
  end

  id = row["id"].to_s.strip
  unless id.empty?
    if ids[id]
      errors << "#{label}: duplicate id '#{id}'"
    else
      ids[id] = true
    end
  end

  type = row["type"].to_s.strip
  errors << "#{label}: invalid type '#{type}'" unless type.empty? || allowed_types.include?(type)

  lang = row["lang"].to_s.strip
  errors << "#{label}: invalid lang '#{lang}'" unless lang.empty? || allowed_langs.include?(lang)

  year = row["year"].to_s.strip
  errors << "#{label}: year must be a 4-digit integer" unless year.match?(/\A\d{4}\z/)

  links = row["links"].to_s.strip
  unless links.empty?
    links.split(";").each do |pair|
      pair_clean = pair.strip
      next if pair_clean.empty?

      if !pair_clean.include?("|")
        errors << "#{label}: invalid links format '#{pair_clean}' (expected Label|URL)"
        next
      end

      label_part, url_part = pair_clean.split("|", 2)
      if label_part.to_s.strip.empty? || url_part.to_s.strip.empty?
        errors << "#{label}: invalid links format '#{pair_clean}' (missing label or URL)"
      end
    end
  end
end

if errors.empty?
  puts "OK: #{rows.size} publications passed schema checks"
  exit 0
end

puts "Validation failed (#{errors.size} error#{errors.size == 1 ? '' : 's'}):"
errors.each { |e| puts "- #{e}" }
exit 1
