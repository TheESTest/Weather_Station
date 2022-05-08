/* Elation Sports Technologies LLC
 * 6 Apr 2022
 * 
 * Wind Speed and Direction
 * 
 * Wind direction sensor:
 * https://www.amazon.com/gp/product/B082YC65W2/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&th=1
 * 
 * Wind speed sensor:
 * https://www.amazon.com/gp/product/B01MZAO4BZ/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1
 * 
 */

int speed_pin = A5;
int dir_pin = A4;
int speed_val = 0;
int dir_val = 0;

const int delay_msec = 1000;

void setup() {
  Serial.begin(9600);
}

void loop() {
  speed_val = analogRead(speed_pin);
  dir_val = analogRead(dir_pin);

  Serial.println(String(dir_val) + "," + String(speed_val));

  delay(delay_msec);
}
