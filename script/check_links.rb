#!/usr/bin/env ruby
# frozen_string_literal: true

require "csv"
require "uri"
require "net/http"
require "openssl"

# Force direct HTTP calls so local proxy env vars do not break checks.
%w[http_proxy https_proxy HTTP_PROXY HTTPS_PROXY all_proxy ALL_PROXY].each do |key|
  ENV.delete(key)
end

DATA_DIR = File.expand_path("../contents/data", __dir__)
TIMEOUT_SECONDS = 8
MAX_REDIRECTS = 5

RESTRICTED_CODES = [401, 403, 405, 407, 408, 409, 410, 412, 413, 414, 415, 416, 418, 421, 423, 425, 426, 429, 451, 500, 502, 503, 504].freeze

RowRef = Struct.new(:file, :row, :label, :url, keyword_init: true)

def follow_request(uri, method:, redirects_left:, visited: {})
  raise URI::InvalidURIError, "missing host" if uri.host.nil?

  key = uri.to_s
  raise "redirect loop" if visited[key]

  visited[key] = true

  http = Net::HTTP.new(uri.host, uri.port)
  http.use_ssl = uri.scheme == "https"
  http.open_timeout = TIMEOUT_SECONDS
  http.read_timeout = TIMEOUT_SECONDS
  http.verify_mode = OpenSSL::SSL::VERIFY_PEER

  path = uri.path.empty? ? "/" : uri.path
  path = [path, uri.query].compact.join("?")

  request = if method == :head
              Net::HTTP::Head.new(path, { "User-Agent" => "jekyll-link-check" })
            else
              Net::HTTP::Get.new(path, { "User-Agent" => "jekyll-link-check" })
            end

  response = http.request(request)
  code = response.code.to_i

  if [301, 302, 303, 307, 308].include?(code)
    location = response["location"].to_s.strip
    return [code, uri] if location.empty? || redirects_left <= 0

    next_uri = URI.join(uri.to_s, location)
    return follow_request(next_uri, method: :get, redirects_left: redirects_left - 1, visited: visited)
  end

  [code, uri]
end

def check_url(url)
  uri = URI.parse(url)

  code, _final_uri = follow_request(uri, method: :head, redirects_left: MAX_REDIRECTS)
  if code >= 400 || code == 405
    code, _final_uri = follow_request(uri, method: :get, redirects_left: MAX_REDIRECTS)
  end

  if code < 400
    [:ok, code]
  elsif RESTRICTED_CODES.include?(code)
    [:restricted, code]
  else
    [:restricted, code]
  end
rescue URI::InvalidURIError => e
  [:invalid_format, e.class.to_s]
rescue StandardError => e
  [:restricted, "#{e.class}: #{e.message}"]
end

entries = []
invalid_format_entries = []

csv_files = Dir[File.join(DATA_DIR, "*.csv")].sort

csv_files.each do |path|
  filename = File.basename(path)
  rows = CSV.read(path, headers: true)
  next unless rows.headers.include?("links")

  rows.each_with_index do |row, idx|
    raw_links = row["links"].to_s.strip
    next if raw_links.empty?

    raw_links.split(";").each do |pair|
      pair_clean = pair.strip
      next if pair_clean.empty?

      unless pair_clean.include?("|")
        invalid_format_entries << RowRef.new(file: filename, row: idx + 2, label: "", url: pair_clean)
        next
      end

      label_part, url_part = pair_clean.split("|", 2)
      label = label_part.to_s.strip
      url = url_part.to_s.strip

      if label.empty? || url.empty?
        invalid_format_entries << RowRef.new(file: filename, row: idx + 2, label: label, url: url)
        next
      end

      unless url.match?(%r{\Ahttps?://}i)
        invalid_format_entries << RowRef.new(file: filename, row: idx + 2, label: label, url: url)
        next
      end

      entries << RowRef.new(file: filename, row: idx + 2, label: label, url: url)
    end
  end
end

if entries.empty? && invalid_format_entries.empty?
  puts "No links found in CSV files"
  exit 0
end

url_status = {}
entries.map(&:url).uniq.each do |url|
  url_status[url] = check_url(url)
end

file_stats = Hash.new { |h, k| h[k] = { total: 0, ok: 0, restricted: 0, invalid_format: 0 } }

entries.each do |ref|
  status, detail = url_status[ref.url]
  file_stats[ref.file][:total] += 1
  file_stats[ref.file][status] += 1
  puts "#{status.to_s.upcase} #{detail} #{ref.file}:#{ref.row} #{ref.url}"
end

invalid_format_entries.each do |ref|
  file_stats[ref.file][:total] += 1
  file_stats[ref.file][:invalid_format] += 1
  puts "INVALID_FORMAT #{ref.file}:#{ref.row} #{ref.url}"
end

puts "\nSummary by file"
file_stats.keys.sort.each do |file|
  stats = file_stats[file]
  puts "- #{file}: total=#{stats[:total]} ok=#{stats[:ok]} restricted=#{stats[:restricted]} invalid_format=#{stats[:invalid_format]}"
end

overall_invalid = invalid_format_entries.size + entries.count { |ref| url_status[ref.url].first == :invalid_format }
overall_restricted = entries.count { |ref| url_status[ref.url].first == :restricted }

puts "\nOverall: checked=#{entries.size} restricted=#{overall_restricted} invalid_format=#{overall_invalid}"

if overall_invalid.positive?
  puts "\nBlocking failure: invalid link formats detected"
  exit 1
end

puts "No blocking issues found"
exit 0
