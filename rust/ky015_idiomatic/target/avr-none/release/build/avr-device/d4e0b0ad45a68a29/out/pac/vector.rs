#[doc(hidden)]
#[macro_export]
macro_rules! __avr_device_trampoline {
    (@atmega328p, RESET, $it:item) => {
        #[export_name = "__vector_0"]
        $it
    };
    (@atmega328p, INT0, $it:item) => {
        #[export_name = "__vector_1"]
        $it
    };
    (@atmega328p, INT1, $it:item) => {
        #[export_name = "__vector_2"]
        $it
    };
    (@atmega328p, PCINT0, $it:item) => {
        #[export_name = "__vector_3"]
        $it
    };
    (@atmega328p, PCINT1, $it:item) => {
        #[export_name = "__vector_4"]
        $it
    };
    (@atmega328p, PCINT2, $it:item) => {
        #[export_name = "__vector_5"]
        $it
    };
    (@atmega328p, WDT, $it:item) => {
        #[export_name = "__vector_6"]
        $it
    };
    (@atmega328p, TIMER2_COMPA, $it:item) => {
        #[export_name = "__vector_7"]
        $it
    };
    (@atmega328p, TIMER2_COMPB, $it:item) => {
        #[export_name = "__vector_8"]
        $it
    };
    (@atmega328p, TIMER2_OVF, $it:item) => {
        #[export_name = "__vector_9"]
        $it
    };
    (@atmega328p, TIMER1_CAPT, $it:item) => {
        #[export_name = "__vector_10"]
        $it
    };
    (@atmega328p, TIMER1_COMPA, $it:item) => {
        #[export_name = "__vector_11"]
        $it
    };
    (@atmega328p, TIMER1_COMPB, $it:item) => {
        #[export_name = "__vector_12"]
        $it
    };
    (@atmega328p, TIMER1_OVF, $it:item) => {
        #[export_name = "__vector_13"]
        $it
    };
    (@atmega328p, TIMER0_COMPA, $it:item) => {
        #[export_name = "__vector_14"]
        $it
    };
    (@atmega328p, TIMER0_COMPB, $it:item) => {
        #[export_name = "__vector_15"]
        $it
    };
    (@atmega328p, TIMER0_OVF, $it:item) => {
        #[export_name = "__vector_16"]
        $it
    };
    (@atmega328p, SPI_STC, $it:item) => {
        #[export_name = "__vector_17"]
        $it
    };
    (@atmega328p, USART_RX, $it:item) => {
        #[export_name = "__vector_18"]
        $it
    };
    (@atmega328p, USART_UDRE, $it:item) => {
        #[export_name = "__vector_19"]
        $it
    };
    (@atmega328p, USART_TX, $it:item) => {
        #[export_name = "__vector_20"]
        $it
    };
    (@atmega328p, ADC, $it:item) => {
        #[export_name = "__vector_21"]
        $it
    };
    (@atmega328p, EE_READY, $it:item) => {
        #[export_name = "__vector_22"]
        $it
    };
    (@atmega328p, ANALOG_COMP, $it:item) => {
        #[export_name = "__vector_23"]
        $it
    };
    (@atmega328p, TWI, $it:item) => {
        #[export_name = "__vector_24"]
        $it
    };
    (@atmega328p, SPM_Ready, $it:item) => {
        #[export_name = "__vector_25"]
        $it
    };
    (@$mcu:ident, $name:ident, $it:item) => {
        compile_error!(concat!("Couldn't find interrupt ", stringify!($name), ", for MCU ", stringify!($mcu), "."));
    }
}
