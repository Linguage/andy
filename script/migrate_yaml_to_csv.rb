#!/usr/bin/env ruby
# frozen_string_literal: true

require "csv"
require "fileutils"
require "yaml"

ROOT = File.expand_path("..", __dir__)
DATA_DIR = File.join(ROOT, "_data")
OUT_DIR = File.join(ROOT, "contents", "data")

FileUtils.mkdir_p(OUT_DIR)


def write_csv(path, headers, rows)
  CSV.open(path, "wb", write_headers: true, headers: headers) do |csv|
    rows.each do |row|
      csv << headers.map { |header| row[header] }
    end
  end
end

publications = YAML.load_file(File.join(DATA_DIR, "publications.yml"))
write_csv(
  File.join(OUT_DIR, "publications.csv"),
  %w[id title year type authors venue links tags lang],
  publications.map do |row|
    links = []
    links << "doi|#{row['doi']}" unless row["doi"].to_s.strip.empty?
    links << "web|#{row['url']}" unless row["url"].to_s.strip.empty?
    links << "pdf|#{row['pdf']}" unless row["pdf"].to_s.strip.empty?

    {
      "id" => row["id"],
      "title" => row["title_en"],
      "year" => row["year"],
      "type" => row["type"],
      "authors" => Array(row["authors"]).join(";"),
      "venue" => row["venue"],
      "links" => links.join(";"),
      "tags" => Array(row["tags"]).join(";"),
      "lang" => row["lang"]
    }
  end
)

teaching = YAML.load_file(File.join(DATA_DIR, "teaching.yml"))
write_csv(
  File.join(OUT_DIR, "teaching_phd.csv"),
  %w[name status period links],
  Array(teaching["phd_students"]).map do |row|
    { "name" => row["name"], "status" => row["status_en"], "period" => row["period"], "links" => "" }
  end
)
write_csv(
  File.join(OUT_DIR, "teaching_master.csv"),
  %w[name status period links],
  Array(teaching["master_students"]).map do |row|
    { "name" => row["name"], "status" => row["status_en"], "period" => row["period"], "links" => "" }
  end
)
write_csv(
  File.join(OUT_DIR, "teaching_courses.csv"),
  %w[code name role links],
  Array(teaching["courses"]).map do |row|
    { "code" => row["code"], "name" => row["name_en"], "role" => row["role_en"], "links" => "" }
  end
)

projects = YAML.load_file(File.join(DATA_DIR, "projects.yml"))
write_csv(
  File.join(OUT_DIR, "projects_research.csv"),
  %w[year title description links],
  Array(projects["research_projects"]).map do |row|
    links = []
    links << "web|#{row['url']}" unless row["url"].to_s.strip.empty?

    {
      "year" => row["year"],
      "title" => row["title_en"],
      "description" => row["description_en"],
      "links" => links.join(";")
    }
  end
)
write_csv(
  File.join(OUT_DIR, "projects_commission.csv"),
  %w[period title links],
  Array(projects["commission_of_trust"]).map do |row|
    { "period" => row["period"], "title" => row["title_en"], "links" => "" }
  end
)

field_testing = YAML.load_file(File.join(DATA_DIR, "field_testing.yml"))
write_csv(
  File.join(OUT_DIR, "field_testing.csv"),
  %w[date year location title notes links],
  field_testing.map do |row|
    {
      "date" => row["date"],
      "year" => row["year"],
      "location" => row["location_en"],
      "title" => row["title_en"],
      "notes" => row["notes_en"],
      "links" => row["map_url"].to_s.strip.empty? ? "" : "map|#{row['map_url']}"
    }
  end
)

cv = YAML.load_file(File.join(DATA_DIR, "cv.yml"))
write_csv(
  File.join(OUT_DIR, "cv_general.csv"),
  %w[affiliation department profile_url],
  [
    {
      "affiliation" => cv.dig("general", "affiliation_en"),
      "department" => cv.dig("general", "department_en"),
      "profile_url" => cv.dig("general", "profile_url")
    }
  ]
)
write_csv(
  File.join(OUT_DIR, "cv_employments.csv"),
  %w[period title org links],
  Array(cv["employments"]).map do |row|
    { "period" => row["period"], "title" => row["title_en"], "org" => row["org"], "links" => "" }
  end
)
write_csv(
  File.join(OUT_DIR, "cv_awards.csv"),
  %w[year item links],
  Array(cv["awards_scholarships"]).map do |row|
    { "year" => row["year"], "item" => row["item_en"], "links" => "" }
  end
)

write_csv(
  File.join(OUT_DIR, "external_profiles.csv"),
  %w[label url],
  [
    { "label" => "ORCiD", "url" => "https://orcid.org/0000-0002-1492-5131" },
    { "label" => "KTH Profile", "url" => "https://www.kth.se/profile/andreasan" },
    { "label" => "DiVA", "url" => "https://www.diva-portal.org/smash/search.jsf?query=Andreas+Andersson+KTH" },
    { "label" => "Google Scholar", "url" => "https://scholar.google.com/citations?user=CmOJmNMAAAAJ" },
    { "label" => "ResearchGate", "url" => "https://www.researchgate.net/profile/Andreas-Andersson-25" }
  ]
)

puts "CSV export complete: #{OUT_DIR}"
