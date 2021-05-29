
document.querySelector('#countryBtn').addEventListener("click", function (evt) {
  evt.preventDefault();
  value = document.querySelector('#countryInput').value;
  window.location.href = `/country/${value}`;
});