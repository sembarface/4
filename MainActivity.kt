package com.example.lab1

import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import kotlin.math.roundToInt

class MainActivity : AppCompatActivity() {

    private lateinit var curNum: EditText
    private lateinit var backNum: TextView
    private lateinit var operationText: TextView

    private var num1 = 0.0
    private var operation = ""

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        curNum = findViewById(R.id.EditTextCur)
        backNum = findViewById(R.id.textViewNum)
        operationText = findViewById(R.id.textViewSign)

        // ===== 1. Обработка цифр (0-9) =====
        val digitButtons = listOf(
            R.id.button0, R.id.button1, R.id.button2, R.id.button3,
            R.id.button4, R.id.button5, R.id.button6, R.id.button7,
            R.id.button8, R.id.button9
        )

        for (id in digitButtons) {
            findViewById<Button>(id).setOnClickListener {
                val digit = (it as Button).text.toString()
                curNum.append(digit)
            }
        }

        // ===== 2. Обработка точки =====
        val btnDot: Button = findViewById(R.id.buttonDot)
        btnDot.setOnClickListener {
            val text = curNum.text.toString()
            if (text.isEmpty()) {
                curNum.append("0.")
            } else if (!text.contains(".")) {
                curNum.append(".")
            }
        }

        // ===== 3. Кнопка "C" (очистка) =====
        val btnCL: Button = findViewById(R.id.buttonC)
        btnCL.setOnClickListener {
            curNum.text.clear()
            backNum.text = ""
            operationText.text = ""
            num1 = 0.0
            operation = ""
        }

        // ===== 4. Кнопка "Del" (удаление символа) =====
        val btnDel: Button = findViewById(R.id.buttonDel)
        btnDel.setOnClickListener {
            val text = curNum.text.toString()
            if (text.isNotEmpty()) {
                curNum.setText(text.substring(0, text.length - 1))
                curNum.setSelection(curNum.text.length)
            }
        }

        // ===== 5. Кнопка "+/-" (смена знака) =====
        val btnNegative: Button = findViewById(R.id.buttonNegative)
        btnNegative.setOnClickListener {
            toggleNegativeSign()
        }

        // ===== 6. Обработчики операций =====
        findViewById<Button>(R.id.buttonPlus).setOnClickListener { handleOperation("+") }
        findViewById<Button>(R.id.buttonMinus).setOnClickListener { handleOperation("-") }
        findViewById<Button>(R.id.buttonDiv).setOnClickListener { handleOperation("/") }
        findViewById<Button>(R.id.buttonMult).setOnClickListener { handleOperation("*") }

        // ===== 7. Кнопка "=" =====
        val btnEq: Button = findViewById(R.id.buttonEquals)
        btnEq.setOnClickListener {
            if (backNum.text.isEmpty() || operation.isEmpty()) {
                showError("Введите операцию")
                return@setOnClickListener
            }

            if (curNum.text.isEmpty()) {
                showError("Введите число")
                return@setOnClickListener
            }

            try {
                val num2 = curNum.text.toString().toDouble()
                var result = 0.0

                // Деление на 0
                if (operation == "/" && num2 == 0.0) {
                    showError("Деление на ноль не допускается")
                    return@setOnClickListener
                }

                when (operation) {
                    "+" -> result = num1 + num2
                    "-" -> result = num1 - num2
                    "*" -> result = num1 * num2
                    "/" -> result = num1 / num2
                }

                if (result % 1.0 == 0.0) {
                    curNum.setText(result.roundToInt().toString())
                } else {
                    curNum.setText(result.toString())
                }

                curNum.setSelection(curNum.text.length)
                backNum.text = ""
                operationText.text = ""
                operation = ""
                num1 = result

            } catch (e: Exception) {
                showError("Ошибка вычислений")
            }
        }
    }

    // Смена знака (+ / -)
    private fun toggleNegativeSign() {
        val currentText = curNum.text.toString()
        if (currentText.isNotEmpty()) {
            if (currentText[0] == '-') {
                curNum.setText(currentText.substring(1))
            } else {
                curNum.setText("-$currentText")
            }
            curNum.setSelection(curNum.text.length)
        }
    }

    // Обработка мат. операций
    private fun handleOperation(op: String) {
        if (curNum.text.isEmpty()) {
            if (backNum.text.isNotEmpty()) {
                operation = op
                operationText.text = operation
            } else {
                showError("Введите число")
            }
            return
        }

        if (backNum.text.isEmpty() && operationText.text.isEmpty()) {
            operation = op
            operationText.text = operation
            backNum.text = curNum.text.toString()
            num1 = curNum.text.toString().toDouble()
            curNum.text.clear()
        } else if (backNum.text.isNotEmpty() && operationText.text.isNotEmpty() && curNum.text.isNotEmpty()) {
            val num2 = curNum.text.toString().toDouble()
            var result = 0.0

            when (operation) {
                "+" -> result = num1 + num2
                "-" -> result = num1 - num2
                "*" -> result = num1 * num2
                "/" -> result = num1 / num2
            }

            if (result % 1.0 == 0.0) {
                backNum.text = result.roundToInt().toString()
            } else {
                backNum.text = result.toString()
            }

            num1 = result
            curNum.text.clear()
            operation = op
            operationText.text = operation
        }
    }

    private fun showError(message: String) {
        curNum.error = message
        curNum.requestFocus()
        Handler(Looper.getMainLooper()).postDelayed({
            curNum.error = null
        }, 1500)
    }
}