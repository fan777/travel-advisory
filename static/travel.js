
document.querySelector('#countryBtn').addEventListener("click", function (evt) {
  evt.preventDefault();
  document.querySelector('#flash_messages').innerHTML = '';
  let value = document.querySelector('#countryInput').value;
  window.location.href = `/country/${value}`;
});