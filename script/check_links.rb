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

file = File.expand_path("../contents/data/publications.csv", __dir__)
rows = CSV.read(file, headers: true)

urls = rows.flat_map do |r|
  links = r["links"].to_s.strip
  next [] if links.empty?

  links.split(";").map do |pair|
    label, url = pair.split("|", 2).map { |part| part.to_s.strip }
    next if label.empty? || url.empty?

    url
  end.compact
end
        .uniq

if urls.empty?
  puts "No external links found in publications.csv"
  exit 0
end

timeout_seconds = 8
failures = []
network_errors = 0

urls.each do |raw|
  begin
    uri = URI.parse(raw)
    raise URI::InvalidURIError, "missing host" if uri.host.nil?

    http = Net::HTTP.new(uri.host, uri.port)
    http.use_ssl = uri.scheme == "https"
    http.open_timeout = timeout_seconds
    http.read_timeout = timeout_seconds
    http.verify_mode = OpenSSL::SSL::VERIFY_PEER

    path = uri.path.empty? ? "/" : uri.path
    path = [path, uri.query].compact.join("?")

    response = http.request(Net::HTTP::Head.new(path, { "User-Agent" => "jekyll-link-check" }))

    if response.code.to_i >= 400
      response = http.request(Net::HTTP::Get.new(path, { "User-Agent" => "jekyll-link-check" }))
    end

    code = response.code.to_i
    status = code < 400 ? "OK" : "FAIL"
    puts "#{status} #{code} #{raw}"
    failures << [raw, code] if code >= 400
  rescue StandardError => e
    puts "FAIL ERR #{raw} (#{e.class}: #{e.message})"
    failures << [raw, e.class.to_s]
    if [SocketError, Errno::ENETUNREACH, Errno::EHOSTUNREACH, Errno::ETIMEDOUT].any? { |klass| e.is_a?(klass) }
      network_errors += 1
    end
  end
end

if failures.empty?
  puts "All #{urls.size} checked links are healthy"
  exit 0
end

if ENV["ALLOW_OFFLINE"] == "1" && network_errors == failures.size
  puts "Offline mode enabled: skipping hard failure for network-only errors"
  exit 0
end

puts "Failed links: #{failures.size}/#{urls.size}"
exit 1
