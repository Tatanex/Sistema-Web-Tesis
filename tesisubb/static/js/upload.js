
$("form").on("change", ".form-control", function() {
  $(this)
    .parent(".campo1, .campo2")
    .attr(
      "data-text",
      $(this)
        .val()
        .replace(/.*(\/|\\)/, "")
    );
});

