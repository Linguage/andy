---
title: Publication Keywords
description: Interactive word cloud for publication keyword filtering.
permalink: /publications/keywords/
---

<section class="card">
  <p>Explore publication keywords from titles and tags, select multiple terms, then open the filtered publications list.</p>
</section>

{% assign publication_count = site.data.publications | size %}
<section
  id="pub-keyword-app"
  class="card keyword-cloud-card"
  data-publications-url="{{ '/publications/' | relative_url }}"
  data-total="{{ publication_count }}"
  style="margin-top: 1rem;"
>
  <div class="keyword-cloud-header">
    <p class="kicker">Interactive filter</p>
    <p id="keyword-cloud-selection" class="meta">No keyword selected.</p>
    <p id="keyword-cloud-match" class="filter-status">{{ publication_count }} publications available.</p>
  </div>

  <div id="keyword-cloud" class="keyword-cloud" aria-live="polite"></div>

  <div class="keyword-cloud-actions">
    <button id="keyword-clear-btn" type="button" class="keyword-cloud-clear">Clear selection</button>
    <a id="keyword-apply-link" class="keyword-cloud-apply" href="{{ '/publications/' | relative_url }}">View filtered publications</a>
  </div>

  <div hidden>
    {% for pub in site.data.publications %}
      {% assign keyword_blob = pub.title | append: ' ' | append: pub.tags %}
      {% assign search_blob = pub.title | append: ' ' | append: pub.authors | append: ' ' | append: pub.venue | append: ' ' | append: pub.tags %}
      <span
        class="pub-keyword-source"
        data-keywords="{{ keyword_blob | downcase | escape }}"
        data-authors="{{ pub.authors | downcase | escape }}"
        data-search="{{ search_blob | downcase | escape }}"
      ></span>
    {% endfor %}
  </div>
</section>

<script src="{{ '/assets/js/publications-keywords.js' | relative_url }}" defer></script>
