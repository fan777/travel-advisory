
document.querySelector('#countryBtn').addEventListener("click", function (evt) {
  evt.preventDefault();
  document.querySelector('#flash_messages').innerHTML = '';
  let value = document.querySelector('#countryInput').value;
  let options = Array.from(document.querySelectorAll('#countryOptions option'));
  let valid = options.map(item => item.value);
  console.log(valid);
  if (!value) {
    document.querySelector('#flash_messages').innerHTML =
      `<div class="alert alert-danger">Search input is empty.</div>`;
  } else if (!valid.includes(value)) {
    document.querySelector('#flash_messages').innerHTML =
      `<div class="alert alert-danger">${value} is not a valid country code!</div>`;
  } else {
    window.location.href = `/country/${value}`;
  }
});

